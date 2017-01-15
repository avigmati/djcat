#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` models module.
"""

from django.test import TestCase

from .models import Category


class CategoryCase(TestCase):

    def test_creation(self):
        """Categories creation test"""
        c = Category.objects.create(title="cat", slug="cat", is_active=True)
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
        c_root = Category.objects.create(title="root", slug="root", parent=None)
        c_child = Category.objects.create(title="child", slug="child", parent=c_root)
        self.assertEqual(c_root.is_root, True)
        self.assertEqual(c_child.parent, c_root)

    def test_child_active_update(self):
        """Categories update children test"""
        c_root = Category.objects.create(title="root", slug="root", parent=None, is_active=True)
        c_child = Category.objects.create(title="child", slug="child", parent=c_root, is_active=True)
        c_root.is_active = False
        c_root.save()
        c_child = Category.objects.get(pk=c_child.pk)
        self.assertEqual(c_child.is_active, False)

    def test_slug_creation(self):
        """Categories slug creation test"""
        c = Category.objects.create(title="привет")
        self.assertEqual(c.slug, 'privet')
        c2 = Category.objects.create(title="привет")
        self.assertNotEqual(c.slug, c2.slug)

    def test_is_unique_in_path(self):
        """Categories unique in path test"""
        c = Category.objects.create(title="test", is_unique_in_path=False, item_class='test_item_class')
        self.assertEqual(c.is_unique_in_path, True)

    def test_paths(self):
        """Categories paths creation and update test"""
        c = Category.objects.create(title="test")
        c.refresh_from_db()
        self.assertEqual(c.get_url_paths(), {'full': ['test'], 'unique': []})
        c1 = Category.objects.create(title="test1", parent=c, is_unique_in_path=True)
        c1.refresh_from_db()
        self.assertEqual(c1.get_url_paths(), {'full': ['test', 'test1'], 'unique': ['test1']})
        c2 = Category.objects.create(title="test2", parent=c1)
        c3 = Category.objects.create(title="test3", parent=c2, item_class='test_item_class')
        c3.refresh_from_db()
        self.assertEqual(c3.get_url_paths(),
                         {'full': ['test', 'test1', 'test2', 'test3'], 'unique': ['test1', 'test3']})

        # create new root and move c1 to this branch
        cn = Category.objects.create(title="test_new")
        cn.refresh_from_db()
        c1.parent = cn
        c1.save()
        c1.refresh_from_db()
        self.assertEqual(c1.get_url_paths(), {'full': ['test_new', 'test1'], 'unique': ['test1']})
        c2.refresh_from_db()
        self.assertEqual(c2.get_url_paths(), {'full': ['test_new', 'test1', 'test2'], 'unique': ['test1']})
        c3.refresh_from_db()
        self.assertEqual(c3.get_url_paths(),
                         {'full': ['test_new', 'test1', 'test2', 'test3'], 'unique': ['test1', 'test3']})
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
