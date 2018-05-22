# coding: utf-8
from os.path import abspath
from os.path import dirname
from os.path import join
import re

from pkg_resources import Requirement
from setuptools import find_packages
from setuptools import setup


_COMMENT_RE = re.compile(r'(^|\s)+#.*$')


def _get_requirements(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = _COMMENT_RE.sub('', line)
            line = line.strip()
            if line.startswith('-r '):
                for req in  _get_requirements(
                    join(dirname(abspath(file_path)), line[3:])
                ):
                    yield req
            elif line:
                req = Requirement(line)
                req_str = req.name + str(req.specifier)
                if req.marker:
                    req_str += '; ' + str(req.marker)
                yield req_str


def _read(file_path):
    with open(file_path, 'r') as infile:
        return infile.read()


setup(
    name='m3-fias',
    url='https://github.com/barsgroup/m3-fias',
    license='MIT',
    author='BARS Group',
    description=u'Федеральная информационная адресная система',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=tuple(_get_requirements('requirements/prod.txt')),
    long_description=_read('README.rst'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
    ],
    extras_require={
        'oauth2': (
            'oauthlib>=2,<3',
            'requests-oauthlib<1',
        ),
    },
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.2,<2',
    ),
    set_build_info=dirname(__file__),
)
