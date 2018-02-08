# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from fabric.api import local
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from six.moves import map


if sys.version_info.major == 2:
    from contextlib import nested  # pylint: disable=unused-import
else:
    from fabric.context_managers import nested  # pylint: disable=unused-import


# Параметры pip, общие для всех команд.
common_pip_params = (
    '--extra-index-url https://pypi.bars-open.ru/simple/',
)


def upgrade_base_packages():
    """Обновляет пакеты pip и setuptools."""
    local('pip install -U pip setuptools')


def install_packages_from_file(file_path, quiet):
    local('pip install{} {} -r {}'.format(
        ' --quiet' if quiet else '',
        ' '.join(common_pip_params),
        file_path,
    ))


def is_package_installed(package):
    try:
        get_distribution(package)
    except DistributionNotFound:
        result = False
    else:
        result = True

    return result


def install_requirements(requirements_file, packages, quiet):
    """Проверяет наличие пакета и при отсутствии устанавливает пакеты из файла.

    :param unicode requirements_file: файл со списком зависимостей.
    :param list packages: список имен пакетов, при отсутствии которых в
        окружении будут установлены пакеты, перечисленные в указанном файле.
    """
    if not all(map(is_package_installed, packages)):
        install_packages_from_file(requirements_file, quiet)
