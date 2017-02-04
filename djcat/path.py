from urllib.parse import urlencode

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from djcat.exceptions import *
from djcat.register import CatalogItem


class Path:
    def __init__(self, path=None, query=None, query_allow_multiple=False, post_dict=None):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)

        self.category = None
        self.item = None
        self.attrs = []
        self.query_allow_multiple = query_allow_multiple
        self.url_full = ''
        self.url_path = ''
        self.url_query = ''

        if path:
            self.path = path
            self._path_list = []
            self.resolve()

        if query:
            self.query = query
            self.parse_query()

        if post_dict:
            self.post_dict = post_dict
            self.parse_post_request()
            self.build_url()

    def get_item(self, slug, item_type='category', item_model=None):
        try:
            if item_type == 'category':
                item = self.CategoryModel.objects.get(slug=slug)
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
                    attrs.append({'attribute': a.class_obj, 'path_value': slug, 'query_value': []})
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
        if self.path:
            self.path = str(self.path)
            self._path_list = [p for p in self.path.split('/') if len(p)]
            if not len(self._path_list):
                self.category = None
                return
        else:
            self.category = None
            return

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
                    branch = self.CategoryModel.objects.get(slug=self._path_list[0]).get_descendants(include_self=True)
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

    def _get_query_attr_classes(self, query):
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
        self.query = self.query.replace('a=', '')

        attrs = self._get_query_attr_classes(self.query)
        for a in attrs:
            attr, query = a[0], a[1]
            value = attr(query=query).parse_query()
            if value:
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

    def parse_post_request(self):
        """
        Parse post_dict.POST parameters
        :return:
        """
        self.category = self.get_category_post()
        if self.category:
            self.attrs = self.get_attrs_post()

    def get_category_post(self):
        """
        Get category instance
        :return: Category model instance
        """
        try:
            category = self.post_dict.get('category', None)
            return self.CategoryModel.objects.get(pk=int(category)) if category else None
        except ObjectDoesNotExist:
            return None

    def get_attrs_post(self):
        """
        Collect and validate category attributes from post_dict.POST parameters
        :return: List of attribute class instances
        """
        item_class = CatalogItem.get_item_by_class(self.category.item_class)
        attrs = []
        for a in item_class.attrs:
            v = self.post_dict.get(a.key, None)
            if v:
                try:
                    attr = a.class_obj(value=v)
                except Exception:
                    pass
                else:
                    attrs.append(attr)
        return attrs

    def build_url(self):
        """
        Build url from category, attributes and other POST parameters
        """
        self.url_path = self.category.get_url() if self.category else ''

        query_dict = {}
        attr_q = []
        attr_keys = []
        for a in self.attrs:
            attr_q.append(a.build_query())
            attr_keys.append(a.attr_key)
        if attr_q:
            query_dict['a'] = '.'.join(attr_q)
        query_dict.update({x[0]: x[1] for x in self.post_dict.items() if x[0] not in ['category'] + attr_keys})
        if query_dict:
            self.url_query = '?' + urlencode(query_dict)

        self.url_full = self.url_path + self.url_query
