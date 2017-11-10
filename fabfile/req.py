# coding: utf-8
from __future__ import unicode_literals

from os.path import join

from fabric.api import local
from fabric.decorators import task

import _settings


# Параметры pip, общие для всех команд.
_common_pip_params = (
    '--extra-index-url https://pypi.bars-open.ru/simple/',
)


def _upgrade_base_packages():
    """Обновляет пакеты pip и setuptools."""
    local('pip install -U pip setuptools')


def _install_packages_from_file(file_path, quiet):
    local('pip install{} {} -r {}'.format(
        ' --quiet' if quiet else '',
        ' '.join(_common_pip_params),
        file_path,
    ))


@task
def delete():
    """Удаление всех пакетов из окружения."""
    local(
        "pip freeze | "
        "egrep -v '\''pkg-resources'\'' | "
        "xargs pip uninstall -y"
    )
    local('pip install --force-reinstall setuptools')


@task
def prod():
    """Обновление списка зависимостей для production-среды."""
    _upgrade_base_packages()

    local('pip install {} -r {}'.format(
        ' '.join(_common_pip_params),
        _settings.REQUIREMENTS_PROD,
    ))


@task
def dev():
    """Обновление списка зависимостей для development-среды."""
    _upgrade_base_packages()

    local('pip install {} -r {}'.format(
        ' '.join(_common_pip_params),
        _settings.REQUIREMENTS_DEV,
    ))


@task
def test():
    """Обновление списка зависимостей для development-среды."""
    _upgrade_base_packages()

    local('pip install {} -r {}'.format(
        ' '.join(_common_pip_params),
        _settings.REQUIREMENTS_TEST,
    ))


@task
def clean():
    """Удаление рабочих файлов."""
    for path in ('.eggs', 'version.conf', 'src/m3_fias.egg-info'):
        local(
            'rm -f -r -d "{path}"'
            .format(
                path=join(_settings.PROJECT_DIR, path),
            )
        )
