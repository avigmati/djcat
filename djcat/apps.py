import pprint

from django.apps import AppConfig

from . import settings
from .__init__ import __version__
from .utils import db_table_exists
from .register import CatalogItem


class DjcatConfig(AppConfig):
    name = 'djcat'

    def ready(self):
        print()
        print('Djcat v{} loading...'.format(__version__))

        c = [x.lower() for x in settings.DJCAT_CATEGORY_MODEL.split('.')]
        category_table_name = '{}_{}'.format(c[0], c[1])
        if db_table_exists(category_table_name):
            CatalogItem.load_items_attributes()
            if settings.DJCAT_DEBUG_OUT == 'file':
                with open(settings.DJCAT_DEBUG_FILE, 'w') as f:
                    f.write('Loaded with structure:\n')
                    f.write(pprint.pformat(CatalogItem.REGISTRY))
            else:
                print('Loaded with structure:')
                pprint.pprint(CatalogItem.REGISTRY)
        else:
            print('Not loaded! Category model "{}" not migrated?'.format(settings.DJCAT_CATEGORY_MODEL))
            print()

