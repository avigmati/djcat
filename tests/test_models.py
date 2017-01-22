#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` models module.
"""

from django.test import TestCase

from catalog.models import Category
from djcat.exceptions import CategoryInheritanceError, CategoryRootCheckError


class TestCategoryCase(TestCase):

    def create_instance(self, **kwargs):
        c = Category.objects.create(**kwargs)
        c.refresh_from_db()
        return c

    def test_creation(self):
        """Categories creation test"""
        c = self.create_instance(title="cat", slug="cat", is_active=True)
        self.assertTrue(isinstance(c, Category))
        self.assertEqual(c.__str__(), c.title)
        self.assertEqual(c.__unicode__(), c.title)
        self.assertEqual(c.is_active, True)
        self.assertEqual(c.is_root, True)
        self.assertEqual(c.is_unique_in_path, False)
        self.assertEqual(c.is_endpoint, False)
        self.assertEqual(c.item_class, None)

    def test_child_creation(self):
        """Categories creation child test"""
        c_root = self.create_instance(title="root", slug="root", parent=None)
        c_child = self.create_instance(title="child", slug="child", parent=c_root)
        self.assertEqual(c_root.is_root, True)
        self.assertEqual(c_child.parent, c_root)

    def test_child_active_update(self):
        """Categories update children test"""
        c_root = self.create_instance(title="root", slug="root", parent=None, is_active=True)
        c_child = self.create_instance(title="child", slug="child", parent=c_root, is_active=True)
        c_root.is_active = False
        c_root.save()
        c_child = Category.objects.get(pk=c_child.pk)
        self.assertEqual(c_child.is_active, False)

    def test_slug_creation(self):
        """Categories slug creation test"""
        c = self.create_instance(title="привет")
        self.assertEqual(c.slug, 'privet')
        c2 = self.create_instance(title="привет2")
        self.assertNotEqual(c.slug, c2.slug)

    def test_is_unique_in_path(self):
        """Categories unique in path test"""
        c = self.create_instance(title="test", is_unique_in_path=False, item_class='test_item_class')
        self.assertEqual(c.is_unique_in_path, True)

    def test_paths(self):
        """Categories paths creation and update test"""
        c = self.create_instance(title="test")
        self.assertEqual(c.get_url_paths(), {'full': ['test'], 'unique': []})
        c1 = self.create_instance(title="test1", parent=c, is_unique_in_path=True)
        self.assertEqual(c1.get_url_paths(), {'full': ['test', 'test1'], 'unique': ['test1']})
        c2 = self.create_instance(title="test2", parent=c1)
        c3 = self.create_instance(title="test3", parent=c2, item_class='test_item_class')
        self.assertEqual(c3.get_url_paths(),
                         {'full': ['test', 'test1', 'test2', 'test3'], 'unique': ['test1', 'test3']})

        # create new root and move c1 to this branch
        cn = self.create_instance(title="test_new")
        c1.parent = cn
        c1.save()
        c1.refresh_from_db()
        c2.refresh_from_db()
        c3.refresh_from_db()
        self.assertEqual(c1.get_url_paths(), {'full': ['test_new', 'test1'], 'unique': ['test1']})
        self.assertEqual(c2.get_url_paths(), {'full': ['test_new', 'test1', 'test2'], 'unique': ['test1']})
        self.assertEqual(c3.get_url_paths(),
                         {'full': ['test_new', 'test1', 'test2', 'test3'], 'unique': ['test1', 'test3']})

    def test_endpoint_as_parent(self):
        c = self.create_instance(title='endpoint', item_class='itemc')
        self.assertRaises(CategoryInheritanceError, self.create_instance, title='fail', parent=c)

    def test_root_with_same_name(self):
        c = self.create_instance(title='root')
        self.assertRaises(CategoryRootCheckError, self.create_instance, title='root')

    def test_move_to_root(self):
        c = self.create_instance(title='root')
        c1 = self.create_instance(title="root", parent=c)
        c1.parent = None
        self.assertRaises(CategoryRootCheckError, c1.save)

# class TestDjcat(TestCase):
#
#     def setUp(self):
#         pass
#
#     def test_something(self):
#         pass
#
#     def tearDown(self):
#         pass
