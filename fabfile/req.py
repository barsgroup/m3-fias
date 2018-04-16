# coding: utf-8
# pylint: disable=duplicate-code
from __future__ import absolute_import
from __future__ import unicode_literals

from os.path import join

from fabric.api import local
from fabric.decorators import task
from pip.commands.uninstall import UninstallCommand
from pip.utils import get_installed_distributions
from six import PY2

from . import _settings
from ._utils import get_dependent_packages
from ._utils import install_requirements


@task
def delete(quiet=False):
    """Удаление всех пакетов из окружения."""
    persistent_packages = {
        'setuptools',
        'wheel',
        'pip',
        'Fabric' if PY2 else 'Fabric3',
    }
    persistent_packages.update(
        get_dependent_packages('Fabric' if PY2 else 'Fabric3')
    )

    params = [
        distribution.project_name
        for distribution in get_installed_distributions()
        if distribution.project_name not in persistent_packages
    ]
    if params:
        params.insert(0, '--yes')
        if not quiet:
            params.insert(0, '--quiet')

        if UninstallCommand().main(params) != 0:
            raise RuntimeError('Package uninstall failed')


@task
def prod(quiet=False):
    """Обновление списка зависимостей для production-среды."""
    install_requirements(_settings.REQUIREMENTS_PROD, quiet)


@task
def dev(quiet=False):
    """Обновление списка зависимостей для development-среды."""
    install_requirements(_settings.REQUIREMENTS_DEV, quiet)


@task
def test(quiet=False):
    """Обновление списка зависимостей для запуска тестов."""
    install_requirements(_settings.REQUIREMENTS_TEST, quiet)


@task
def clean():
    """Удаление рабочих файлов."""
    for path in ('.eggs', 'version.conf', 'src/m3_d15n.egg-info'):
        local(
            'rm -f -r -d "{path}"'
            .format(
                path=join(_settings.PROJECT_DIR, path),
            )
        )
