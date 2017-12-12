# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from itertools import imap

from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution


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
    from req import _install_packages_from_file

    if not all(imap(is_package_installed, packages)):
        _install_packages_from_file(requirements_file, quiet)
