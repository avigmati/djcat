# -*- coding: utf-8
from django.apps import AppConfig
from django.conf import settings


class DjcatConfig(AppConfig):
    name = 'djcat'

    def ready(self):
        if settings.DEBUG:
            from pprint import pprint
            from .__init__ import __version__
            from .register import CatalogItem
            print()
            print('Djcat v{} loading...'.format(__version__))
            if settings.DJCAT_INIT_ATTR:
                CatalogItem.load_items_attributes()
                print('Loaded with structure:')
                pprint(CatalogItem.REGISTRY)
