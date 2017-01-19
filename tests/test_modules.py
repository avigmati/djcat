#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_djcat
------------

Tests for `djcat` catalog modules module.
"""

from django.test import TestCase

from djcat.models import CatalogItem
from djcat.exceptions import CategoryInheritanceError, CategoryRootCheckError


class ModulesCase(TestCase):

    def test_modules_load(self):
        """Modules load test"""
        mstruct = {
            'ModuleA':
                {
                    'items':
                        {'ItemA':
                             {'attributes':
                                  {'AttributeA':
                                       {'class': 'module_a.attrs.AttributeA',
                                        'key': 'aa',
                                        'verbose_name': 'Attribute A'}
                                   },
                              'class': 'module_a.models.ItemA',
                              'verbose_name': 'Item A'
                              }
                         },
                    'module': 'module_a.models',
                    'verbose_name': 'Module A'
                }
        }
        self.assertTrue(mstruct == CatalogItem.REGISTRY)
