from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from djcat.exceptions import *
from djcat.register import CatalogItem


class Path:
    def __init__(self, path=None, query=None, query_allow_multiple=False):
        self._CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)

        self.category = None
        self.item = None
        self.attrs = []
        self.query_allow_multiple = query_allow_multiple

        self.path = path
        self._path_list = []
        self.resolve()

        if query:
            self.query = query
            self.parse_query()

    def get_item(self, slug, item_type='category', item_model=None):
        try:
            if item_type == 'category':
                item = self._CategoryModel.objects.get(slug=slug)
            else:
                item = item_model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise PathNotFound(self.path)
        return item

    def get_category_paths(self, node):
        """
        Return category instance url paths converted to list
        :param node: Category instance
        :return: List of paths
        """
        return list(node.get_url_paths().values())

    def get_category_attr_paths(self, node):
        """
        Return list of all category attributes slugs
        :param node: Category instance
        :return: List of attributes slugs
        """
        if not node.item_class:
            return []
        item = CatalogItem.get_item_by_class(node.item_class)
        paths = []
        for a in item.attrs:
            if a.type == 'choice':
                paths.extend(a.choices)
        return paths

    def check_slug_category(self, slug, category_paths):
        """
        Return True if slug in category paths
        :param slug: String slug
        :param category_paths: List of category paths
        :return: Bool
        """
        paths = list(set([x for paths in category_paths for x in paths]))
        return slug in paths

    def check_slug_attr(self, slug, attr_paths):
        """
        Return True if slug in category attributes paths
        :param slug: String slug
        :param attr_paths: List of category attributes paths
        :return: Bool
        """
        return slug in attr_paths

    def get_attrs(self, node, resolved_attr_slugs):
        """
        Return resolved attribute with selected slug
        :param node: Category instance
        :param resolved_attr_slugs: List of resolved slugs
        :return: List of dictionaries
        """
        attrs = []
        item = CatalogItem.get_item_by_class(node.item_class)
        for slug in resolved_attr_slugs:
            for a in item.attrs:
                if a.choices and slug in a.choices:
                    attrs.append({'attribute': a.class_obj, 'path_value': slug})
        return attrs

    def get_item_instance(self, category_slug, item_slug):
        """
        Return True if slug in category attributes paths
        :param slug: String slug
        :param attr_paths: List of category attributes paths
        :return: Bool
        """
        self.category = self.get_item(category_slug)
        _item = CatalogItem.get_item_by_class(self.category.item_class)
        self.item = self.get_item(item_slug, item_type='item', item_model=_item.class_obj)

    def resolve_mix_path(self, category_paths, attr_paths):
        """
        Resolve path that probably contain category paths (slugs) and category attributes paths (slugs)
        :param category_paths: List of category paths
        :param attr_paths: List of category attributes paths
        :return:
        """
        if len(self._path_list) > 1 and len(self._path_list[-1].split('_')) == 2:
            pass

        resolved = []
        for slug in self._path_list:
            if self.check_slug_category(slug, category_paths):
                resolved.append({'category': slug})
                continue
            if self.check_slug_attr(slug, attr_paths):
                resolved.append({'attr': slug})
                continue
        if not len(resolved) == len(self._path_list):
            raise PathNotFound(self.path)
        return resolved

    def resolve(self):
        """
        Obtain elements of path: category, item. attributes
        :return:
        """
        self._path_list = [p for p in self.path.split('/') if len(p)] if self.path else []
        if not len(self._path_list):
            raise PathNotValid(self.path)

        if len(self._path_list) == 1:
            """
            one element in path can only be a category
            """
            self.category = self.get_item(self._path_list[0])

        else:
            if len(self._path_list) > 1 and len(self._path_list[-1].split('_')) == 2:
                """
                if last element contain "_" then it is item slug, and last by one is item category
                """
                self.get_item_instance(self._path_list[-2], self._path_list[-1])
            else:
                try:
                    branch = self._CategoryModel.objects.get(slug=self._path_list[0]).get_descendants(include_self=True)
                except ObjectDoesNotExist:
                    raise PathNotFound(self.path)
                for node in branch:
                    category_paths = self.get_category_paths(node)
                    if self._path_list in category_paths:
                        self.category = node
                        break
                    else:
                        attr_paths = self.get_category_attr_paths(node)
                        if not len(attr_paths):
                            continue
                        resolved = self.resolve_mix_path(category_paths, attr_paths)
                        self.category = node
                        self.attrs = self.get_attrs(node, [x['attr'] for x in resolved if x.get('attr')])

    def _get_query_attr_clases(self, query):
        """
        Find and return attributes what found in query string
        :param query: String, query
        :return: Dict of attribute classes and his query
        """
        item_class = CatalogItem.get_item_by_class(self.category.item_class)
        attrs = []
        _query_attrs = []

        for qa in [x for x in query.split('.') if len(x)]:
            _qa = qa.split('_')
            if not len(_qa) == 2:
                continue
            _query_attrs.append((_qa[0], _qa[1]))

        for a in _query_attrs:
            for ia in item_class.attrs:
                if a[0] == ia.key:
                    if not self.query_allow_multiple:
                        if ia.class_obj not in [x[0] for x in attrs]:
                            attrs.append((ia.class_obj, a[1]))
                    else:
                        attrs.append((ia.class_obj, a[1]))
        return attrs

    def parse_query(self):
        """
        Parse query
        :param query: String, query
        :return:
        """
        attrs = self._get_query_attr_clases(self.query)
        for a in attrs:
            attr, query = a[0], a[1]
            value = attr(query=query).parse_query()
            resolved = False
            if self.attrs:
                for _a in self.attrs:
                    if _a['attribute'] == attr:
                        _a['query_value'].append(value)
                        resolved = True
                if not resolved:
                    self.attrs.append({'attribute': attr, 'query_value': [value]})
            else:
                self.attrs.append({'attribute': attr, 'query_value': [value]})
