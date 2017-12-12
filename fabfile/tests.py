# coding: utf-8
# pylint: disable=not-context-manager, relative-import
from __future__ import absolute_import
from __future__ import unicode_literals

from contextlib import nested
import os

from ._utils import install_requirements
from fabric.api import local
from fabric.context_managers import lcd
from fabric.context_managers import settings
from fabric.decorators import task

from . import _settings


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
