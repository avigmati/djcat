#!/usr/bin/env python

import os, sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
sys.path.insert(0, BASE_DIR)

try:
    from django.conf import settings
    from django.core.management import call_command
    from django.test.utils import get_runner
except ImportError:
    import traceback
    traceback.print_exc()
    msg = "To fix this error, run: pip install -r requirements_test.txt"
    raise ImportError(msg)


def setup_proj():
    try:
        from test_settings import settings as test_settings
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        settings.configure(**test_settings)
        setup()


def run_tests(*test_args):

    setup_proj()

    if not test_args:
        test_args = ['tests']

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(bool(failures))


if __name__ == '__main__':
    # first migrate
    os.system(os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrate_test_project.py"))
    # then run tests
    run_tests(*sys.argv[1:])
