# coding: utf-8
from os.path import abspath
from os.path import dirname
from os.path import join
import os

import django

BASE_DIR = dirname(dirname(abspath(__file__)))

SECRET_KEY = 'SECRET_KEY'

DEBUG = True

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE_CLASSES = []

INSTALLED_APPS = [
    'django.contrib.staticfiles',

    'm3',
    'm3_ext',
    'm3_fias',

    'test_project.test_app',
]

ROOT_URLCONF = 'test_project.urls'

local_template_packages = (
    ('m3_ext', 'ui/templates'),
)
if django.VERSION < (1, 8):
    TEMPLATE_DIRS = list(set(
        (
            join(path, relative_path)
            if relative_path else
            dirname(path)
        )
        for name, relative_path in local_template_packages
        for path in __import__(name).__path__
    ))
    TEMPLATE_CONTEXT_PROCESSORS = [
        'django.template.context_processors.debug',
        'django.template.context_processors.media',
        'django.template.context_processors.static',
        'django.template.context_processors.request',
    ]
else:
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': list(set(
                (
                    join(path, relative_path)
                    if relative_path else
                    dirname(path)
                )
                for name, relative_path in local_template_packages
                for path in __import__(name).__path__
            )),
            'OPTIONS': {
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ],
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.request',
                ]
            },
        },
    ]

WSGI_APPLICATION = 'test_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

STATIC_URL = '/static/'

if django.VERSION < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'
# -----------------------------------------------------------------------------
# Параметры ФИАС.

FIAS = {
    'BACKEND': os.environ['FIAS_BACKEND'],
}

if FIAS['BACKEND'] == 'm3_fias.backends.django_rest_fias.proxy':

    FIAS_DRF_SERVER_MOCK = os.environ.get('FIAS_DRF_SERVER_MOCK', '') == 'True'
    if FIAS_DRF_SERVER_MOCK:
        def _get_free_port():
            import socket
            s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
            s.bind(('127.0.0.1', 0))
            _, port = s.getsockname()
            s.close()
            return port

        DRF_SERVER_PORT = _get_free_port()
        FIAS['URL'] = 'http://127.0.0.1:{}'.format(DRF_SERVER_PORT)
    else:
        FIAS['URL'] = 'http://fias.bars-open.ru/fias/v1/ao/'

    FIAS['USE_CACHE'] = os.environ['FIAS_USE_CACHE'] == 'True'
