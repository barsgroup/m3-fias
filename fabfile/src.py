# coding: utf-8
from __future__ import unicode_literals

from contextlib import nested
from itertools import imap
from os.path import join

from fabric.api import local
from fabric.colors import green
from fabric.context_managers import lcd
from fabric.context_managers import settings
from fabric.context_managers import shell_env
from fabric.decorators import task
from fabric.tasks import execute

import _settings


@task
def isort():
    """Сортировка импортов в модулях проекта."""
    with lcd(_settings.PROJECT_DIR):
        print green('isort', bold=True)

        source_directories = (
            _settings.SRC_DIR,
            _settings.TESTS_DIR,
            join(_settings.PROJECT_DIR, 'fabfile'),
        )
        local(
            'isort --skip= --settings-path "{}" -rc {}'.format(
                join(_settings.PROJECT_DIR, '.isort.cfg'),
                ' '.join(
                    imap(lambda s: '"{}"'.format(s), source_directories)
                ),
            )
        )


@task
def pep8():
    """Проверка стилевого оформления кода проекта."""
    with nested(
        settings(ok_ret_codes=(0, 1)),
        lcd(_settings.PROJECT_DIR),
    ):
        print green('PEP-8', bold=True)

        local(
            'pycodestyle {SRC_DIR}'
            .format(
                SRC_DIR=_settings.SRC_DIR,
            )
        )


@task
def pylint():
    """Проверка кода проекта с помощью PyLint."""
    with nested(
        settings(ok_ret_codes=(0, 1, 4, 30)),
        lcd(_settings.PROJECT_DIR),
        shell_env(PYTHONPATH=_settings.SRC_DIR),
    ):
        print green('PyLint', bold=True)

        local(
            'pylint --rcfile={PROJECT_DIR}/pylint.rc {PROJECT_PACKAGE}'
            .format(
                PROJECT_DIR=_settings.PROJECT_DIR,
                PROJECT_PACKAGE=_settings.PROJECT_PACKAGE,
            )
        )


@task(default=True)
def run_all():
    """Запуск всех проверок src.*."""
    execute(isort)
    execute(pep8)
    execute(pylint)


@task
def clean():
    """Удаление ненужных файлов."""
    for dir_path in (
        join(_settings.PROJECT_DIR, 'src'),
        join(_settings.PROJECT_DIR, 'tests'),
        join(_settings.PROJECT_DIR, 'fabfile'),
    ):
        for pattern in ('*.pyc', '__pycache__'):
            local(
                'find "{dir_path}" -name {pattern} -delete'
                .format(
                    dir_path=dir_path,
                    pattern=pattern,
                )
            )
