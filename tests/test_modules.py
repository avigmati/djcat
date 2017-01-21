#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` catalog modules module.
"""

from django.test import TestCase

from djcat.register import CatalogItem
from djcat.exceptions import *


class ModulesCase(TestCase):
    """Modules load test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loaded = CatalogItem.REGISTRY
        self.module = self.loaded.get('Realty')
        self.item = self.module.get('items').get('FlatBuy')

    def test_load_catalog(self):
        """Test modules and items
            {'Realty': {'_module': '',
                   'items': {'FlatBuy': {'_class': '',
                                         'attrs': {},
                                         'class': 'catalog_module_realty.models.FlatBuy',
                                         'verbose_name': 'Куплю квартиру'}},
                   'module': 'catalog_module_realty.models',
                   'verbose_name': 'Недвижимость'}}
        """
        self.assertTrue(isinstance(self.loaded, dict))
        self.assertTrue(self.module, dict)
        self.assertTrue(self.module.get('module'), 'catalog_module_realty.models')
        self.assertTrue(self.module.get('verbose_name'), 'Недвижимость')
        self.assertTrue(self.module.get('items'), dict)
        self.assertTrue(self.item, dict)
        self.assertTrue(self.item.get('class'), 'catalog_module_realty.models.FlatBuy')
        self.assertTrue(self.item.get('verbose_name'), 'Куплю квартиру')

    def test_simply_attribute(self):
        """Test simply attribute of catalog item
            'price': {'_class': <catalog.attrs.PriceAttribute object at 0x7fc548dfb208>,
                      'class': 'catalog.attrs.PriceAttribute',
                      'key': 'pr',
                      'type': 'simply',
                      'verbose_name': 'Цена'}}
        """
        self.item_attrs = self.item.get('attrs')
        self.assertTrue(isinstance(self.item_attrs, dict))
        attr = self.item_attrs.get('price')
        self.assertTrue(attr, dict)
        self.assertTrue(attr.get('class'), 'catalog.attrs.PriceAttribute')
        self.assertTrue(attr.get('key'), 'pr')
        self.assertTrue(attr.get('type'), 'simply')
        self.assertTrue(attr.get('verbose_name'), 'Цена')

    def test_choice_attribute(self):
        """Test simply attribute of catalog item
            'building_type': {'_class': <catalog_module_realty.attrs.BuildingTypeAttribute object at 0x7f04890c8208>,
                              'class': 'catalog_module_realty.attrs.BuildingTypeAttribute',
                              'key': 'rbt',
                              'type': 'choice',
                              'choices': ['kirpichnuy',
                                          'panelnuy',
                                          'blochnuy',
                                          'monolitnuy',
                                          'derevyanuy'],
                              'verbose_name': 'Тип '
                                              'строения'},
        """
        self.item_attrs = self.item.get('attrs')
        attr = self.item_attrs.get('building_type')
        self.assertTrue(attr, dict)
        self.assertTrue(attr.get('class'), 'catalog_module_realty.attrs.BuildingTypeAttribute')
        self.assertTrue(attr.get('key'), 'rbt')
        self.assertTrue(attr.get('type'), 'choice')
        self.assertTrue(len(attr.get('choices')), 5)
