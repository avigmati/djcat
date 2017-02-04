import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')

settings = dict(
    BASE_DIR=BASE_DIR,
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

    DJCAT_CATEGORY_MODEL='catalog.Category',
    DJCAT_CATALOG_ROOT_URL='/'
)

