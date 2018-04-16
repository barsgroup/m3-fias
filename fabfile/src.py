# coding: utf-8
# pylint: disable=no-name-in-module, ungrouped-imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from itertools import chain
from os import walk
from os.path import dirname
from os.path import join

from fabric.api import local
from fabric.colors import green
from fabric.colors import red
from fabric.context_managers import hide
from fabric.context_managers import lcd
from fabric.context_managers import settings
from fabric.context_managers import shell_env
from fabric.decorators import task
from fabric.tasks import execute
from fabric.utils import abort
from six import PY2

from . import _settings
from ._utils import fix_file_coding
from ._utils import get_coding_declaration
from ._utils import require


if PY2:
    from contextlib import nested
else:
    from fabric.context_managers import nested


@task
def coding(check_only=None):
    """Приведение объявления кодировки py-файлов к единому стилю."""
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print(green('Encoding declarations', bold=True))
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    source_dirs = (
        _settings.SRC_DIR,
        _settings.TESTS_DIR,
        dirname(__file__,)
    )
    files = chain(
        (
            join(root, file_name)
            for path in source_dirs
            for root, _, file_names in walk(path)
            for file_name in file_names
            if file_name.endswith('.py')
        ),
        (
            join(_settings.PROJECT_DIR, 'setup.py'),
        ),
    )
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for file_path in files:
        valid, header = get_coding_declaration(file_path)
        if not valid:
            if valid is None:
                header = '[NOT SPECIFIED]'
            print('{}: {}'.format(file_path, red(header.strip())))
            if check_only != 'yes':
                fix_file_coding(file_path)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@task
@require('isort')
def isort(check_only=None):
    """Сортировка импортов в модулях проекта.

    :param str check_only: только проверка модулей.
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print(green('isort', bold=True))
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    config_path = join(_settings.SRC_DIR, '.isort.cfg')
    params = [
        'isort',
        '--skip=',
        '--settings-path "{}"'.format(config_path),
    ]
    if check_only == 'yes':
        params.append('--check-only')
    params.append('-rc')
    params.extend((
        join(_settings.SRC_DIR, 'm3_d15n'),
        dirname(__file__),
        join(_settings.PROJECT_DIR, 'setup.py'),
    ))
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    out = local(' '.join(params))
    if out.return_code != 0:
        print('isort return code:', out.return_code)
        abort('failed')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@task
@require('pycodestyle')
def style():
    """Проверка стилевого оформления кода проекта."""
    print(green(u'Code style check', bold=True))
    out = local(
        'pycodestyle --config={SRC_DIR}/setup.cfg {SRC_DIR}'
        .format(
            SRC_DIR=_settings.SRC_DIR,
        )
    )
    if out.return_code != 0:
        print('pycodestyle return code:', out.return_code)
        abort('failed')


@task
@require('pydocstyle')
def doc():
    """Проверка правильности оформления строк документации."""
    print(green(u'Docstrings check', bold=True))
    out = local('pydocstyle ' + _settings.PROJECT_DIR)
    if out.return_code != 0:
        print('pydocstyle return code:', out.return_code)
        abort('failed')


@task
@require('pylint', 'oauthlib', 'requests_oauthlib')
def pylint():
    """Проверка кода проекта с помощью PyLint."""
    print(green(u'Pylint', bold=True))
    with nested(
        hide('running'),
        settings(ok_ret_codes=(0, 1, 4, 30)),
        lcd(_settings.PROJECT_DIR),
        shell_env(PYTHONPATH=_settings.SRC_DIR),
    ):
        source_dirs = ' '.join(
            '"{}"'.format(dir_path)
            for dir_path in (
                join(_settings.SRC_DIR, _settings.PROJECT_PACKAGE),
                _settings.TESTS_DIR,
                join(_settings.PROJECT_DIR, 'fabfile')
            )
        )

        if local('pylint --py3k ' + source_dirs).return_code != 0:
            abort('Python 3 incompartible')

        if local(
            'pylint "--rcfile={}/pylint.rc" {}'.format(
                _settings.PROJECT_DIR, source_dirs
            )
        ).return_code != 0:
            abort('Pylint checks failed')


@task(default=True)
def run_all():
    """Запуск всех проверок src.*."""
    execute(coding)
    execute(isort)
    execute(style)
    execute(pylint)


@task
def clean():
    """Удаление ненужных файлов."""
    for dir_name in ('src', 'tests', 'fabfile'):
        for pattern in ('*.pyc', '__pycache__'):
            local(
                'find "{dir_path}" -name {pattern} -delete'
                .format(
                    dir_path=join(_settings.PROJECT_DIR, dir_name),
                    pattern=pattern,
                )
            )
