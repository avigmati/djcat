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
        self.assertEqual(path.attrs[0]['attribute'].name, 'building_type')
        self.assertEqual(path.attrs[0]['selected_value'], 'kirpichnyi')

    def test_check_category_instance_with_two_attr(self):
        c = self.create_category(name="Недвижимость", is_active=True)
        c1 = self.create_category(name="Квартиры", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Куплю", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')

        path = Path(path='kvartiry/kupliu/kirpichnyi/studio')
        self.assertEqual(path.category, c2)
        self.assertEqual(path.attrs[0]['attribute'].name, 'building_type')
        self.assertEqual(path.attrs[0]['selected_value'], 'kirpichnyi')
        self.assertEqual(path.attrs[1]['attribute'].name, 'room')
        self.assertEqual(path.attrs[1]['selected_value'], 'studio')

