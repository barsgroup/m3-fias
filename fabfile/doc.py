# coding: utf-8
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
def api():
    """Генерация документации по API."""
    if not is_packages_installed('sphinx'):
        install_requirements(_settings.REQUIREMENTS_DEV, quiet=True)

    with lcd(_settings.DOCS_DIR):  # pylint: disable=not-context-manager
        output_path = join(_settings.DOCS_DIR, 'source', 'api')
        exclude = (
            join(_settings.SRC_DIR, _settings.PROJECT_PACKAGE, 'migrations'),
            join(_settings.SRC_DIR, _settings.PROJECT_PACKAGE, 'apps.py'),
        )

        local('rm -f -r "{}"'.format(output_path))

        local(
            'sphinx-apidoc {options} -o "{output}" "{module}" {exclude}'
            .format(
                options=' '.join((
                    '--separate',
                    '--no-toc',
                )),
                output=output_path,
                module=_settings.SRC_DIR,
                exclude=' '.join('"' + path + '"' for path in exclude),
            )
        )


@task
def build():
    """Сборка документации."""
    if not is_packages_installed('sphinx'):
        install_requirements(_settings.REQUIREMENTS_DEV, quiet=True)

    with lcd(_settings.DOCS_DIR):  # pylint: disable=not-context-manager
        local('make html')


@task
def browser():
    """Открытие собранной документации в браузере."""
    INDEX_HTML = join(_settings.DOCS_DIR, 'build', 'html', 'index.html')

    local('xdg-open {}'.format(INDEX_HTML))


@task
def server():
    """Запуск веб-сервера для автогенерации и просмотра документации."""
    if not is_packages_installed('sphinx', 'sphinx-autobuild'):
        install_requirements(_settings.REQUIREMENTS_DEV, quiet=True)

    with lcd(_settings.DOCS_DIR):  # pylint: disable=not-context-manager
        local(u'make livehtml')


@task
def clean():
    """Удаление рабочих файлов Sphinx."""
    local(
        'rm -f -r -d "{build_dir}"'
        .format(
            build_dir=join(_settings.DOCS_DIR, 'build'),
        )
    )

    local(
        'find "{docs_dir}" -name *.pyc -delete'
        .format(
            docs_dir=_settings.DOCS_DIR,
        )
    )
