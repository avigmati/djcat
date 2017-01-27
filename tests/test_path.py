#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` catalog path.
"""

from django.test import TestCase

from django.apps import apps
from django.conf import settings

from djcat.path import Path
from djcat.register import CatalogItem
from djcat.exceptions import *


class TestPathCase(TestCase):
    """Path test"""

    def create_category(self, **kwargs):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        c = self.CategoryModel.objects.create(**kwargs)
        c.refresh_from_db()
        return c

    def test_path_args(self):
        """Test modules and items
            {'Realty': {'_module': '',
                   'items': {'FlatBuy': {'_class': '',
                                         'attrs': {},
                                         'class': 'catalog_module_realty.models.FlatBuy',
                                         'verbose_name': 'Куплю квартиру'}},
                   'module': 'catalog_module_realty.models',
                   'verbose_name': 'Недвижимость'}}
        """
        self.assertRaises(PathNotValid, Path, path=None)
        self.assertRaises(PathNotValid, Path, path='')
        self.assertRaises(PathNotValid, Path, path='/')
        self.assertRaises(PathNotValid, Path, path='//')
        self.assertRaises(PathNotFound, Path, path='/sdgsdgf/')

    def test_check_category_instance(self):
        c = self.create_category(name="Недвижимость", is_active=True)
        c1 = self.create_category(name="Квартиры", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Куплю", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')
        self.assertEqual(c2.get_url_paths(),
                         {'full': ['nedvizhimost', 'kvartiry', 'kupliu'], 'unique': ['kvartiry', 'kupliu']})

        path = Path(path='/nedvizhimost/')
        self.assertEqual(path.category, c)

        path = Path(path='/nedvizhimost/kvartiry/kupliu')
        self.assertEqual(path.category, c2)

        path = Path(path='kvartiry/kupliu')
        self.assertEqual(path.category, c2)

    def test_check_category_instance_with_one_attr(self):
        c = self.create_category(name="Недвижимость", is_active=True)
        c1 = self.create_category(name="Квартиры", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Куплю", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')

        path = Path(path='kvartiry/kupliu/kirpichnyi')
        self.assertEqual(path.category, c2)
        self.assertEqual(path.attrs[0]['attribute'].attr_name, 'building_type')
        self.assertEqual(path.attrs[0]['path_value'], 'kirpichnyi')

    def test_check_category_instance_with_two_attr(self):
        c = self.create_category(name="Недвижимость", is_active=True)
        c1 = self.create_category(name="Квартиры", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Куплю", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')

        path = Path(path='kvartiry/kupliu/kirpichnyi/studio')
        self.assertEqual(path.category, c2)
        self.assertEqual(path.attrs[0]['attribute'].attr_name, 'building_type')
        self.assertEqual(path.attrs[0]['path_value'], 'kirpichnyi')
        self.assertEqual(path.attrs[1]['attribute'].attr_name, 'room')
        self.assertEqual(path.attrs[1]['path_value'], 'studio')

    def test_check_item_instance(self):
        c = self.create_category(name="Недвижимость", is_active=True)
        c1 = self.create_category(name="Квартиры", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Куплю", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')

        item_class = CatalogItem.get_item_by_class(c2.item_class)
        item = item_class.class_obj.objects.create(category=c2,  price=11,
                                                   building_type=1, room=2)

        path = Path(path='kvartiry/kupliu/'+item.slug)
        self.assertEqual(path.category, c2)
        self.assertEqual(path.item, item)

    def test_check_query(self):
        c = self.create_category(name="Недвижимость", is_active=True)
        c1 = self.create_category(name="Квартиры", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Куплю", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')

        item_class = CatalogItem.get_item_by_class(c2.item_class)
        item = item_class.class_obj.objects.create(category=c2,  price=11,
                                                   building_type=1, room=2)


        # realpath: 'kvartiry/kupliu?a=pr_f100-t10000000'
        path = Path(path='kvartiry/kupliu/', query='pr_f100-t10000000.pr_f5-t15', query_allow_multiple=True)
        # path = Path(path='kvartiry/kupliu/', query='pr_f100-t10000000.pr_f5-t15', query_allow_multiple=False)
        print()
        # path.get_query_attrs(query='pr_f100-t10000000')
        # print()
        # path1 = Path(path='kvartiry/kupliu/kirpichnyi', query='rbt_1,2,3')
        # print()
        # path2 = Path(path='kvartiry/kupliu/', query='rbt_1-3')
        # print()
        # path3 = Path(path='kvartiry/kupliu/kirpichnyi', query='rbt_kirpichnyi')
        # print()
        # path4 = Path(path='kvartiry/kupliu/', query='rbt_custom')
        # print()
        # print()




        # path = Path(path='kvartiry/kupliu/'+item.slug)
