from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from djcat.exceptions import *
from djcat.register import CatalogItem


class Path:
    def __init__(self, path=None):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        self.in_path = path
        self.category = None
        self.attrs = None
        self.path_list = []
        self.resolve()

    def get_item(self, slug, item_type='category'):
        try:
            item = self.CategoryModel.objects.get(slug=slug) if item_type == 'category' else ''
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

    def resolve_mix_path(self, category_paths, attr_paths):
        """
        Resolve path that probably contain category paths (slugs) and category attributes paths (slugs)
        :param category_paths: List of category paths
        :param attr_paths: List of category attributes paths
        :return:
        """
        resolved = []
        for slug in self.path_list:
            if self.check_slug_category(slug, category_paths):
                resolved.append({'category': slug})
            if self.check_slug_attr(slug, attr_paths):
                resolved.append({'attr': slug})
        if not len(resolved) == len(self.path_list):
            raise PathNotFound(self.in_path)
        return resolved

    def resolve(self):
        self.path_list = [p for p in self.in_path.split('/') if len(p)] if self.in_path else []
        if not len(self.path_list):
            raise PathNotValid(self.in_path)
        if len(self.path_list) == 1:
            self.category = self.get_item(self.path_list[0])
        else:
            try:
                branch = self.CategoryModel.objects.get(slug=self.path_list[0]).get_descendants(include_self=True)
            except ObjectDoesNotExist:
                raise PathNotFound(self.in_path)
            for node in branch:
                category_paths = self.get_category_paths(node)
                if self.path_list in category_paths:
                    self.category = node
                    break
                else:
                    attr_paths = self.get_category_attr_paths(node)
                    if not len(attr_paths):
                        continue
                    resolved = self.resolve_mix_path(category_paths, attr_paths)
                    self.category = node
                    self.attrs = self.get_attrs(node, [x['attr'] for x in resolved if x.get('attr')])
                    print()
