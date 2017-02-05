#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` catalog modules module.
"""

from django.test import TestCase

from djcat.register import CatalogItem


class TestModulesCase(TestCase):
    """Modules test, see structure in djcat_debug.txt"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loaded = CatalogItem.REGISTRY
        self.module = self.loaded.get('Realty')
        self.item = self.module.get('items').get('FlatBuy')

    def test_load_catalog(self):
        """Test modules and items"""

        self.assertTrue(isinstance(self.loaded, dict))
        self.assertTrue(isinstance(self.module, dict))
        self.assertEqual(self.module.get('module'), 'catalog_module_realty.models')
        self.assertEqual(self.module.get('verbose_name'), 'Realty')
        self.assertTrue(isinstance(self.module.get('items'), dict))
        self.assertTrue(isinstance(self.item, dict))
        self.assertEqual(self.item.get('class'), 'catalog_module_realty.models.FlatBuy')
        self.assertEqual(self.item.get('verbose_name'), 'Flat buy')

    def test_simply_attribute(self):
        """Test numeric attribute of catalog item"""

        self.item_attrs = self.item.get('attrs')
        self.assertTrue(isinstance(self.item_attrs, dict))
        attr = self.item_attrs.get('price')
        self.assertTrue(isinstance(attr, dict))
        self.assertEqual(attr.get('class'), 'catalog.attrs.PriceAttribute')
        self.assertEqual(attr.get('key'), 'pr')
        self.assertEqual(attr.get('type'), 'numeric')
        self.assertEqual(attr.get('verbose_name'), 'Price')

    def test_choice_attribute(self):
        """Test choice attribute of catalog item"""

        self.item_attrs = self.item.get('attrs')
        attr = self.item_attrs.get('building_type')
        self.assertTrue(isinstance(attr, dict))
        self.assertEqual(attr.get('class'), 'catalog_module_realty.attrs.BuildingTypeAttribute')
        self.assertEqual(attr.get('key'), 'rbt')
        self.assertEqual(attr.get('type'), 'choice')
        self.assertEqual(len(attr.get('choices')), 5)

    def test_get_item_by_class(self):
        item = CatalogItem.get_item_by_class('catalog_module_realty.models.FlatBuy')
        self.assertEqual(item.name, 'FlatBuy')

