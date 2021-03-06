#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` catalog view.
"""

from django.test import TestCase, Client

from django.apps import apps
from django.conf import settings

import json

from djcat.register import CatalogItem
from djcat.exceptions import *


class TestViewCase(TestCase):
    """Catalog.views.Catalog view test"""

    def create_category(self, **kwargs):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        c = self.CategoryModel.objects.create(**kwargs)
        c.refresh_from_db()
        return c

    def setUp(self):
        self.client = Client()
        c = self.create_category(name="Realty", is_active=True)
        c1 = self.create_category(name="Flat", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Flatbuy", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')

        item_class = CatalogItem.get_item_by_class(c2.item_class)
        self.item = item_class.class_obj.objects.create(category=c2,  price=11,
                                                        building_type=1, room=2)

    def test_catalog_view_get_category(self):
        response = self.client.get('')
        self.assertEqual(response.context.get('category'), '')

        response = self.client.get('/flat/flatbuy')
        self.assertEqual(response.context.get('category'), '')

        response = self.client.get('/flat/flatbuy/')
        self.assertEqual(response.context.get('category'), 'Flatbuy')

        response = self.client.get('/flat/flatbuy/?a=pr_f1-t50')
        self.assertEqual(response.context.get('category'), 'Flatbuy')
        self.assertEqual(response.context.get('pr'), [{'to': 50, 'from': 1}])

        response = self.client.get('/flat/flatbuy/?a=pr_f1-t50&q=hello')
        self.assertEqual(response.context.get('category'), 'Flatbuy')
        self.assertEqual(response.context.get('pr'), [{'to': 50, 'from': 1}])
        self.assertEqual(response.context.get('q'), 'hello')

    def test_catalog_view_get_item(self):
        response = self.client.get('/flat/flatbuy/'+self.item.slug+'/')
        self.assertEqual(response.context.get('item'), self.item.name)

    def test_catalog_view_post(self):
        response = self.client.post('/flat/', {'category': 0}, follow=True)
        self.assertEqual(response.context.get('category'), '')

        response = self.client.post('/flat/', {'category': 3}, follow=True)
        self.assertEqual(response.context.get('category'), 'Flatbuy')

        pr = json.dumps({'from': 1, 'to': 50})
        rbt = json.dumps([1, 2, 4])
        response = self.client.post('/flat/', {'category': 3, 'pr': pr, 'rbt': rbt, 'q': 'hello'}, follow=True)
        self.assertEqual(response.context.get('category'), 'Flatbuy')
        self.assertEqual(response.context.get('pr'), [{'to': 50, 'from': 1}])
        self.assertEqual(response.context.get('rbt'), [[1, 2, 4]])
        self.assertEqual(response.context.get('q'), 'hello')
