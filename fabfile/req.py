# coding: utf-8
from fabric.api import local
from fabric.decorators import task

import _settings


# Параметры pip, общие для всех команд.
_common_pip_params = (
    '--extra-index-url https://pypi.bars-open.ru/simple/',
)


def _upgrade_base_packages():
    u"""Обновляет пакеты pip и setuptools."""
    local(u'pip install -U pip setuptools fabric')


@task
def clean():
    u"""Удаление всех пакетов из окружения."""
    local(
        "pip freeze | "
        "egrep -v '\''pkg-resources'\'' | "
        "xargs pip uninstall -y"
    )
    local('pip install --force-reinstall setuptools fabric')


@task
def prod():
    u"""Обновление списка зависимостей для production-среды."""
    _upgrade_base_packages()

    local(u'pip install {} -r {}'.format(
        u' '.join(_common_pip_params),
        _settings.REQUIREMENTS_PROD,
    ))


@task
def dev():
    u"""Обновление списка зависимостей для development-среды."""
    _upgrade_base_packages()

    local(u'pip install {} -r {}'.format(
        u' '.join(_common_pip_params),
        _settings.REQUIREMENTS_DEV,
    ))
