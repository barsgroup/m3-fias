# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from os.path import join

from fabric.api import local
from fabric.decorators import task

from . import _settings
from ._utils import common_pip_params
from ._utils import upgrade_base_packages


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
    upgrade_base_packages()

    local('pip install {} -r {}'.format(
        ' '.join(common_pip_params),
        _settings.REQUIREMENTS_PROD,
    ))


@task
def dev():
    """Обновление списка зависимостей для development-среды."""
    upgrade_base_packages()

    local('pip install {} -r {}'.format(
        ' '.join(common_pip_params),
        _settings.REQUIREMENTS_DEV,
    ))


@task
def test():
    """Обновление списка зависимостей для development-среды."""
    upgrade_base_packages()

    local('pip install {} -r {}'.format(
        ' '.join(common_pip_params),
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
