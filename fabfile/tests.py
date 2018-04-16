# coding: utf-8
# pylint: disable=not-context-manager, relative-import, duplicate-code
from __future__ import absolute_import
from __future__ import unicode_literals

from os.path import join

from fabric.api import local
from fabric.context_managers import lcd
from fabric.decorators import task

from . import _settings
from ._utils import install_requirements
from ._utils import is_packages_installed


@task
def run():
    """Запуск веб-сервера разработки Django."""
    if not is_packages_installed('tox'):
        install_requirements(_settings.REQUIREMENTS_DEV, quiet=True)

    with lcd(_settings.PROJECT_DIR):
        local(u'tox')


@task
def clean():
    """Удаляет файлы, создаваемые при запуске тестов."""
    local(
        'rm -f -r -d "{project_root}"'
        .format(
            project_root=join(_settings.PROJECT_DIR, '.tox'),
        )
    )
