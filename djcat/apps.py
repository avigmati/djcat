# -*- coding: utf-8
from django.apps import AppConfig
from django.conf import settings


class DjcatConfig(AppConfig):
    name = 'djcat'

    def ready(self):
        if settings.DEBUG:
            from pprint import pprint
            from .__init__ import __version__
            from .models import CatalogItem
            print()
            print('Djcat {} loaded with structure:'.format(__version__))
            pprint(CatalogItem.REGISTRY)
            print()

