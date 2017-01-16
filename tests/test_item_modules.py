#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` models module.
"""

from django.test import TestCase

from djcat.utils import get_item_modules


class ItemModulesCase(TestCase):
    # pass

    def test_get_item_modules(self):
        """Item modules get list test"""
        self.assertTrue('Realty' in get_item_modules())
