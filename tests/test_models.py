#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` models module.
"""

from django.test import TestCase

from django.apps import apps
from django.conf import settings

from djcat.register import CatalogItem
from djcat.exceptions import *


class TestCategoryCase(TestCase):

    def create_instance(self, **kwargs):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        c = self.CategoryModel.objects.create(**kwargs)
        c.refresh_from_db()
        return c

    def test_creation(self):
        """Categories creation test"""

        c = self.create_instance(name="cat", slug="cat", is_active=True)
        self.assertTrue(isinstance(c, self.CategoryModel))
        self.assertEqual(c.__str__(), c.name)
        self.assertEqual(c.__unicode__(), c.name)
        self.assertEqual(c.is_active, True)
        self.assertEqual(c.is_root, True)
        self.assertEqual(c.is_unique_in_path, False)
        self.assertEqual(c.is_endpoint, False)
        self.assertEqual(c.item_class, None)

    def test_child_creation(self):
        """Categories creation child test"""

        c_root = self.create_instance(name="root", slug="root", parent=None)
        c_child = self.create_instance(name="child", slug="child", parent=c_root)
        self.assertEqual(c_root.is_root, True)
        self.assertEqual(c_child.parent, c_root)

    def test_child_active_update(self):
        """Categories update children test"""

        c_root = self.create_instance(name="root", slug="root", parent=None, is_active=True)
        c_child = self.create_instance(name="child", slug="child", parent=c_root, is_active=True)
        c_root.is_active = False
        c_root.save()
        c_child = self.CategoryModel.objects.get(pk=c_child.pk)
        self.assertEqual(c_child.is_active, False)

    def test_slug_creation(self):
        """Categories slug creation test"""

        c = self.create_instance(name="hello")
        self.assertEqual(c.slug, 'hello')

    def test_is_unique_in_path(self):
        """Categories unique in path test"""

        c = self.create_instance(name="test", is_unique_in_path=False, item_class='test_item_class')
        self.assertEqual(c.is_unique_in_path, True)

    def test_paths(self):
        """Categories paths creation and update test"""

        c = self.create_instance(name="test")
        self.assertEqual(c.get_url_paths(), {'full': ['test'], 'unique': []})
        c1 = self.create_instance(name="test1", parent=c, is_unique_in_path=True)
        self.assertEqual(c1.get_url_paths(), {'full': ['test', 'test1'], 'unique': ['test1']})
        c2 = self.create_instance(name="test2", parent=c1)
        c3 = self.create_instance(name="test3", parent=c2, item_class='test_item_class')
        self.assertEqual(c3.get_url_paths(),
                         {'full': ['test', 'test1', 'test2', 'test3'], 'unique': ['test1', 'test3']})

        # create new root and move c1 to this branch
        cn = self.create_instance(name="test new")
        c1.parent = cn
        c1.save()
        c1.refresh_from_db()
        c2.refresh_from_db()
        c3.refresh_from_db()
        self.assertEqual(c1.get_url_paths(), {'full': ['testnew', 'test1'], 'unique': ['test1']})
        self.assertEqual(c2.get_url_paths(), {'full': ['testnew', 'test1', 'test2'], 'unique': ['test1']})
        self.assertEqual(c3.get_url_paths(),
                         {'full': ['testnew', 'test1', 'test2', 'test3'], 'unique': ['test1', 'test3']})

    def test_endpoint_as_parent(self):
        c = self.create_instance(name='endpoint', item_class='itemc')
        self.assertRaises(CategoryInheritanceError, self.create_instance, name='fail', parent=c)

    def test_root_with_same_name(self):
        c = self.create_instance(name='root')
        self.assertRaises(CategoryRootCheckError, self.create_instance, name='root')

    def test_slugs_uniques(self):
        c = self.create_instance(name='test cat')
        c2 = self.create_instance(name='test cat', parent=c)
        self.assertEqual(c.slug, 'testcat')
        self.assertEqual(c2.slug, 'testcat-1')

    def test_move_to_root(self):
        c = self.create_instance(name='root')
        c1 = self.create_instance(name="root", parent=c)
        c1.parent = None
        self.assertRaises(CategoryRootCheckError, c1.save)

    def test_slug_clashes_with_attrs_slugs(self):
        self.assertEqual(self.create_instance(name='Brick', slug='brick',
                                              item_class='catalog_module_realty.models.FlatBuy').slug,
                         'brick-1')


class TestItemCase(TestCase):

    def create_category(self, **kwargs):
        self.CategoryModel = apps.get_model(settings.DJCAT_CATEGORY_MODEL)
        c = self.CategoryModel.objects.create(**kwargs)
        c.refresh_from_db()
        return c

    def test_item_create(self):
        c = self.create_category(name="Realty", is_active=True)
        c1 = self.create_category(name="Flat", parent=c, is_unique_in_path=True, is_active=True)
        c2 = self.create_category(name="Flatbuy", parent=c1, is_active=True,
                                  item_class='catalog_module_realty.models.FlatBuy')
        item_class = CatalogItem.get_item_by_class(c2.item_class)
        item = item_class.class_obj.objects.create(category=c2,  price=11,
                                                   building_type=1, room=2)
        self.assertTrue(isinstance(item, item_class.class_obj))

