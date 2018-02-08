# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from os.path import join
import sys

from fabric.api import local
from fabric.colors import green
from fabric.context_managers import lcd
from fabric.context_managers import settings
from fabric.context_managers import shell_env
from fabric.decorators import task
from fabric.tasks import execute
from fabric.utils import abort

from ._settings import PROJECT_DIR
from ._settings import PROJECT_PACKAGE
from ._settings import SRC_DIR
from ._settings import TESTS_DIR
from ._utils import nested


@task
def isort():
    """Сортировка импортов в модулях проекта."""
    with lcd(PROJECT_DIR):  # pylint: disable=not-context-manager
        print(green('isort', bold=True))

        source_directories = (
            SRC_DIR,
            TESTS_DIR,
            join(PROJECT_DIR, 'fabfile'),
        )
        local(
            'isort --skip= --settings-path "{}" -rc {}'.format(
                join(PROJECT_DIR, '.isort.cfg'),
                ' '.join(
                    '"{}"'.format(dir_path)
                    for dir_path in source_directories
                ),
            )
        )


@task
def style():
    """Проверка стилевого оформления кода проекта."""
    with nested(
        settings(ok_ret_codes=(0, 1)),
        lcd(PROJECT_DIR),
    ):
        print(green('PEP-8', bold=True))

        local(
            'pycodestyle {SRC_DIR}'
            .format(
                SRC_DIR=SRC_DIR,
            )
        )


@task
def pylint():
    """Проверка кода проекта с помощью PyLint."""
    with nested(
        settings(ok_ret_codes=(0, 1, 4, 30)),
        lcd(PROJECT_DIR),
        shell_env(PYTHONPATH=SRC_DIR),
    ):
        source_dirs = ' '.join(
            '"{}"'.format(dir_path)
            for dir_path in (
                join(SRC_DIR, PROJECT_PACKAGE),
                TESTS_DIR,
                join(PROJECT_DIR, 'fabfile')
            )
        )

        print((green(u'PyLint (compartibility mode)', bold=True)))
        if sys.version_info.major == 2:
            cmd = 'python -3 -Werror -m compileall ' + source_dirs
        else:
            cmd = 'python -m compileall ' + source_dirs
        if local(cmd).return_code != 0:
            abort('Python 3 incompartible')
        if local('pylint --py3k ' + source_dirs).return_code != 0:
            abort('Python 3 incompartible')

        print((green(u'PyLint', bold=True)))
        if local(
            'pylint "--rcfile={}/pylint.rc" {}'.format(
                PROJECT_DIR, source_dirs
            )
        ).return_code != 0:
            abort('Pylint checks failed')


@task(default=True)
def run_all():
    """Запуск всех проверок src.*."""
    execute(isort)
    execute(style)
    execute(pylint)


@task
def clean():
    """Удаление ненужных файлов."""
    for dir_path in (
        join(PROJECT_DIR, 'src'),
        join(PROJECT_DIR, 'tests'),
        join(PROJECT_DIR, 'fabfile'),
    ):
        for pattern in ('*.pyc', '__pycache__'):
            local(
                'find "{dir_path}" -name {pattern} -delete'
                .format(
                    dir_path=dir_path,
                    pattern=pattern,
                )
            )
