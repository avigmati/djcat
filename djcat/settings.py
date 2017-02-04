import os
from django.conf import settings


DJCAT_DEBUG_OUT = getattr(settings, 'DJCAT_DEBUG_OUT', "file")
DJCAT_DEBUG_FILE = getattr(settings, 'DJCAT_DEBUG_FILE', os.path.join(settings.BASE_DIR, 'djcat_debug.txt'))
DJCAT_ATTR_TYPES = getattr(settings, 'DJCAT_ATTR_TYPES', ['numeric', 'choice'])
DJCAT_ITEM_SLUG_DELIMITER = getattr(settings, 'DJCAT_ITEM_SLUG_DELIMITER', '_')
DJCAT_ITEM_UID_LENGTH = getattr(settings, 'DJCAT_ITEM_UID_LENGTH', 8)

DJCAT_CATEGORY_MODEL = getattr(settings, 'DJCAT_CATEGORY_MODEL')
DJCAT_CATALOG_ROOT_URL = getattr(settings, 'DJCAT_CATALOG_ROOT_URL')


# DJCAT_ATTR_TYPES = ['numeric', 'choice']
# DJCAT_CATEGORY_MODEL = 'catalog.Category'
# DJCAT_ITEM_SLUG_DELIMETER = '_'
# DJCAT_ITEM_UID_LENGTH = 8
# DJCAT_CATALOG_ROOT_URL = 'catalog/'