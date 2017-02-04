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
    ROOT_URLCONF="tests.urls",

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

    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],

    # DJCAT_INIT_ATTR=False,
    DJCAT_DEBUG_OUT='file',
    DJCAT_DEBUG_FILE=os.path.join(BASE_DIR, 'djcat_debug.txt'),
    DJCAT_ATTR_TYPES=['numeric', 'choice'],
    DJCAT_CATEGORY_MODEL='catalog.Category',
    DJCAT_ITEM_SLUG_DELIMETER='_',
    DJCAT_ITEM_UID_LENGTH=8,
    DJCAT_CATALOG_ROOT_URL='/'
)

def settings_for_migrate():
    _settings = copy.deepcopy(settings)
    _settings['DJCAT_INIT_ATTR'] = False
    return _settings

def settings_for_test():
    _settings = copy.deepcopy(settings)
    _settings['DJCAT_INIT_ATTR'] = True
    return _settings
