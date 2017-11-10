# coding: utf-8
from __future__ import unicode_literals

from os.path import join

from fabric.context_managers import cd
from fabric.decorators import task
from fabric.operations import local
from fabric.tasks import execute

import _settings
import doc
import req
import src
import tests


@task
def clean():
    """Полная очистка от рабочих файлов."""
    execute(doc.clean)
    execute(req.clean)
    execute(src.clean)
    execute(tests.clean)

    with cd(_settings.PROJECT_DIR):
        for path in ('.eggs', 'dist'):
            local(
                'rm -f -r -d "{project_dir}"'
                .format(
                    project_dir=join(_settings.PROJECT_DIR, path),
                )
            )

        local('git gc --quiet')
