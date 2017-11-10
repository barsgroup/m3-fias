#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals

from os import environ
from os.path import abspath
from os.path import dirname
from os.path import join
import sys


if __name__ == '__main__':
    BASE_DIR = dirname(dirname(abspath(__file__)))
    SRC_PATH = join(BASE_DIR, 'src')
    TESTS_PATH = join(BASE_DIR, 'tests')

    sys.path.insert(0, SRC_PATH)
    environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            __import__('django')
        except ImportError:
            raise ImportError(
                'Couldn''t import Django. Are you sure it''s installed and '
                'available on your PYTHONPATH environment variable? Did you '
                'forget to activate a virtual environment?'
            )
        raise

    execute_from_command_line(sys.argv)
