import os
import copy

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

settings = dict(
    DEBUG=True,
    USE_TZ=True,
    DATABASES={
        "default": {
            'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    ROOT_URLCONF="djcat.urls",

    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sites",
        "mptt",
        "djcat",
        "catalog",
        "catalog_module_realty"
    ],
    SITE_ID=1,
    MIDDLEWARE_CLASSES=(),

    DJCAT_INIT_ATTR=False,
    DJCAT_ATTR_TYPES=['simply', 'choice'],
    DJCAT_CATEGORY_MODEL='catalog.Category',
    DJCAT_ITEM_SLUG_DELIMETER='_',
    DJCAT_ITEM_UID_LENGTH=8
)

def settings_for_migrate():
    _settings = copy.deepcopy(settings)
    _settings['DJCAT_INIT_ATTR'] = False
    return _settings

def settings_for_test():
    _settings = copy.deepcopy(settings)
    _settings['DJCAT_INIT_ATTR'] = True
    return _settings
