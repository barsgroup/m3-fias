# coding: utf-8
from __future__ import unicode_literals

from os.path import join

from fabric.api import local
from fabric.context_managers import lcd
from fabric.decorators import task

import _settings


@task
def build():
    """Сборка документации."""
    with lcd(_settings.DOCS_DIR):
        local(u'make html')


@task
def browser():
    """Открытие собранной документации в браузере."""
    INDEX_HTML = join(_settings.DOCS_DIR, 'build', 'html', 'index.html')

    local('xdg-open {}'.format(INDEX_HTML))


@task
def server():
    """Запуск веб-сервера для автогенерации и просмотра документации."""
    with lcd(_settings.DOCS_DIR):
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
