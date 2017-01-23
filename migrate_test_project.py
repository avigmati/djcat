#!/usr/bin/env python

import os, sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
sys.path.insert(0, BASE_DIR)

try:
    import django
    from django.conf import settings
    from django.core.management import call_command
except ImportError:
    import traceback
    traceback.print_exc()
    msg = "To fix this error, run: pip install -r requirements_test.txt"
    raise ImportError(msg)


try:
    setup = django.setup
    from test_settings import settings_for_migrate
    settings.configure(**settings_for_migrate())
except AttributeError:
    pass
else:
    setup()
    call_command('migrate')
    call_command('makemigrations', 'catalog')
    call_command('makemigrations', 'catalog_module_realty')
    call_command('migrate', 'catalog')
    call_command('migrate', 'catalog_module_realty')

