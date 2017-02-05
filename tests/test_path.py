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

    def setUp(self):
        self.c = self.create_category(name="Realty", is_active=True)
        self.c1 = self.create_category(name="Flat", parent=self.c, is_unique_in_path=True, is_active=True)
        self.c2 = self.create_category(name="Flatbuy", parent=self.c1, is_active=True,
                                       item_class='catalog_module_realty.models.FlatBuy')
        self.item_class = CatalogItem.get_item_by_class(self.c2.item_class)
        self.item = self.item_class.class_obj.objects.create(category=self.c2,  price=11,
                                                             building_type=1, room=2)

    def create_category(self, **kwargs):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        c = self.CategoryModel.objects.create(**kwargs)
        c.refresh_from_db()
        return c

    def test_bad_args(self):
        """Test path resolver with bad args"""

        self.assertEqual(Path(path=None).category, None)
        self.assertEqual(Path(path='').category, None)
        self.assertEqual(Path(path='/').category, None)
        self.assertEqual(Path(path='//').category, None)
        self.assertEqual(Path(path='/sdgsdgf/').category, None)

    def test_resolve_category(self):
        """Test path resolver with category path only"""

        self.assertEqual(self.c2.get_url_paths(),
                         {'full': ['realty', 'flat', 'flatbuy'], 'unique': ['flat', 'flatbuy']})
        path = Path(path='/realty/')
        self.assertEqual(path.category, self.c)
        path = Path(path='/realty/flat/flatbuy')
        self.assertEqual(path.category, self.c2)
        path = Path(path='flat/flatbuy')
        self.assertEqual(path.category, self.c2)
        path = Path(path='flatbuy')
        self.assertEqual(path.category, self.c2)

    def test_resolve_category_and_attrs(self):
        """Test path resolver with category and  path attributes"""

        path = Path(path='flat/flatbuy/brick/asdfasdfasdfasdf')
        self.assertEqual(path.category, None)

        path = Path(path='flat/flatbuy/brick')
        self.assertEqual(path.category, self.c2)
        self.assertEqual(path.attrs[0]['attribute'].attr_name, 'building_type')
        self.assertEqual(path.attrs[0]['path_value'], 'brick')

        path = Path(path='flat/flatbuy/brick/1roomed')
        self.assertEqual(path.category, self.c2)
        self.assertEqual(path.attrs[0]['attribute'].attr_name, 'building_type')
        self.assertEqual(path.attrs[0]['path_value'], 'brick')
        self.assertEqual(path.attrs[1]['attribute'].attr_name, 'rooms')
        self.assertEqual(path.attrs[1]['path_value'], '1roomed')

    def test_resolve_item_instance(self):
        """Test path resolver with item"""
        path = Path(path='flat/flatbuy/'+self.item.slug)
        self.assertEqual(path.category, self.c2)
        self.assertEqual(path.item, self.item)

    def test_parse_query(self):
        """Test resolve & parse query"""

        path = Path(path='flat/flatbuy/', query='pr_f100-t500.pr_t15', query_allow_multiple=True)
        self.assertEqual(path.attrs[0]['query_value'][0], {'from': 100, 'to': 500})
        self.assertEqual(path.attrs[0]['query_value'][1], {'to': 15})

        path = Path(path='flat/flatbuy/brick', query='rbt_22')
        self.assertEqual(path.attrs[0]['path_value'], 'brick')
        self.assertEqual(path.attrs[0]['query_value'], [])

        path = Path(path='flat/flatbuy/brick', query='rbt_2')
        self.assertEqual(path.attrs[0]['query_value'], [2])

        path = Path(path='flat/flatbuy/brick', query='rbt_1,2,3')
        self.assertEqual(path.attrs[0]['query_value'], [[1,2,3]])
        path = Path(path='flat/flatbuy/brick', query='rbt_1,2,3,10')
        self.assertEqual(path.attrs[0]['query_value'], [])
        path = Path(path='flat/flatbuy/brick', query='rbt_1-5')
        self.assertEqual(path.attrs[0]['query_value'], [])

    def test_build_query_from_value(self):
        """Test attribute build query string"""

        a = self.item_class.get_attr_by_key('pr').class_obj()
        v = a.build_query({'from': 100, 'to': 567})
        self.assertEqual(v, 'pr_f100-t567')
        v = a.build_query({'from': 100})
        self.assertEqual(v, 'pr_f100')

        a = self.item_class.get_attr_by_key('rbt').class_obj()
        v = a.build_query([1, 2, 3])
        self.assertEqual(v, 'rbt_1,2,3')
