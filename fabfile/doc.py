# coding: utf-8
from os.path import join

from fabric.api import local
from fabric.context_managers import lcd
from fabric.decorators import task

from . import _settings


@task
def build():
    u"""Сборка документации."""
    with lcd(_settings.DOCS_DIR):
        local(u'make html')


@task
def browser():
    u"""Открытие собранной документации в браузере."""
    INDEX_HTML = join(_settings.DOCS_DIR, 'build', 'html', 'index.html')

    local('xdg-open {}'.format(INDEX_HTML))


@task
def server():
    u"""Запуск веб-сервера для автогенерации и просмотра документации."""
    with lcd(_settings.DOCS_DIR):
        local(u'make livehtml')
