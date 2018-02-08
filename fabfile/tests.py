# coding: utf-8
# pylint: disable=not-context-manager, relative-import
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from fabric.api import local
from fabric.context_managers import lcd
from fabric.context_managers import settings
from fabric.context_managers import shell_env
from fabric.decorators import task

from . import _settings
from ._utils import install_requirements
from ._utils import nested


@task
def app(backend='m3_fias.backends.django_rest_fias.proxy'):
    """Запуск тестового веб-приложения."""
    with nested(
        shell_env(
            PYTHONPATH=':'.join((
                _settings.SRC_DIR,
                _settings.TESTS_DIR,
            )),
            FIAS_BACKEND=backend,
            FIAS_USE_CACHE='True',
        ),
        lcd(_settings.TESTS_DIR),
    ):
        local('python manage.py runserver')


@task
def shell(backend='m3_fias.backends.django_rest_fias.proxy'):
    """Запуск тестового веб-приложения."""
    with nested(
        shell_env(
            PYTHONPATH=':'.join((
                _settings.SRC_DIR,
                _settings.TESTS_DIR,
            )),
            FIAS_BACKEND=backend,
            FIAS_USE_CACHE='True',
        ),
        lcd(_settings.TESTS_DIR),
    ):
        local('python manage.py shell')


@task
def run():
    """Запуск тестов в текущем окружении."""
    with nested(
        lcd(_settings.PROJECT_DIR),
        settings(ok_ret_codes=(0, 1)),
    ):
        local('coverage erase')
        local(
            'coverage run '
            '--source src/m3_fias '
            'tests/manage.py test'
        )
        local('coverage report --show-missing')


@task
def tox():
    """Запуск тестов через tox."""
    install_requirements(
        packages=('tox',),
        requirements_file=_settings.REQUIREMENTS_TEST,
        quiet=True,
    )

    if 'PYTHONPATH' in os.environ:
        del os.environ['PYTHONPATH']

    with nested(
        lcd(_settings.PROJECT_DIR),
        settings(ok_ret_codes=(0, 1)),
    ):
        local('coverage erase')
        local('tox')
        local('coverage report --show-missing')


@task
def clean():
    """Удаляет файлы, создаваемые при запуске тестов."""
    with lcd(_settings.PROJECT_DIR):
        local('rm -f -r -d "{}"'.format('.tox'))
        local('rm -f .coverage')
