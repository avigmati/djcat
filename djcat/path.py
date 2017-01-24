from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from djcat.exceptions import *
from djcat.register import CatalogItem


class Path:
    def __init__(self, path=None):
        self._CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        self.in_path = path
        self.category = None
        self.item = None
        self.attrs = None
        self._path_list = []
        self.resolve()

    def get_item(self, slug, item_type='category', item_model=None):
        try:
            if item_type == 'category':
                item = self._CategoryModel.objects.get(slug=slug)
            else:
                item = item_model.objects.get(slug=slug)
        except ObjectDoesNotExist:
            raise PathNotFound(self.in_path)
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
                    attrs.append({'attribute': a, 'selected_value': slug})
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
            raise PathNotFound(self.in_path)
        return resolved

    def resolve(self):
        """
        Obtain elements of path: category, item. attributes
        :return:
        """
        self._path_list = [p for p in self.in_path.split('/') if len(p)] if self.in_path else []
        if not len(self._path_list):
            raise PathNotValid(self.in_path)

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
                    raise PathNotFound(self.in_path)
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

