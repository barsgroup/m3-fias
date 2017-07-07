# coding: utf-8
from contextlib import nested

from fabric.api import local
from fabric.colors import green
from fabric.context_managers import hide
from fabric.context_managers import lcd
from fabric.context_managers import settings
from fabric.context_managers import shell_env
from fabric.decorators import task
from fabric.tasks import execute

import _settings


@task
def isort():
    u"""Сортировка импортов в модулях проекта."""
    with nested(
        hide('running'),
        lcd(_settings.PROJECT_DIR),
    ):
        print green(u'isort', bold=True)
        print

        local(
            'isort -rc {SRC_DIR}'
            .format(
                SRC_DIR=_settings.SRC_DIR,
            )
        )


@task
def pep8():
    u"""Проверка стилевого оформления кода проекта."""
    with nested(
        hide('running'),
        settings(ok_ret_codes=(0, 1)),
        lcd(_settings.PROJECT_DIR),
    ):
        print green(u'PEP-8', bold=True)
        print

        local(
            'pep8 --config={SRC_DIR}/setup.cfg {SRC_DIR}'
            .format(
                SRC_DIR=_settings.SRC_DIR,
            )
        )


@task
def pylint():
    u"""Проверка кода проекта с помощью PyLint."""
    with nested(
        hide('running'),
        settings(ok_ret_codes=(0, 1, 4, 30)),
        lcd(_settings.PROJECT_DIR),
        shell_env(PYTHONPATH=_settings.SRC_DIR),
    ):
        print green(u'PyLint', bold=True)
        print

        local(
            'pylint --rcfile={SRC_DIR}/pylint.rc {PROJECT_PACKAGE}'
            .format(
                SRC_DIR=_settings.SRC_DIR,
                PROJECT_PACKAGE=_settings.PROJECT_PACKAGE,
            )
        )


@task(default=True)
def run_all():
    u"""Запуск всех проверок src.*."""
    execute(isort)
    execute(pep8)
    execute(pylint)
