#!/usr/bin/env python

import os, sys
from django.core.management import call_command


try:
    from django.conf import settings
    from django.test.utils import get_runner

    BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    MODULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests', 'item_modules')
    sys.path.insert(0, MODULES_DIR)

    settings.configure(
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
            "module_a"
        ],
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(),

    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()
        call_command('migrate')
        call_command('makemigrations', 'module_a')
        call_command('migrate')

except ImportError:
    import traceback
    traceback.print_exc()
    msg = "To fix this error, run: pip install -r requirements_test.txt"
    raise ImportError(msg)


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
