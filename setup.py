# coding: utf-8
from os import chdir
from os.path import abspath
from os.path import dirname
from os.path import isabs
from os.path import join
from os.path import relpath

from pip.download import PipSession
from pip.req.req_file import parse_requirements
from setuptools import find_packages
from setuptools import setup


def _get_requirements(file_path):
    pip_session = PipSession()
    requirements = parse_requirements(file_path, session=pip_session)

    return tuple(str(requirement.req) for requirement in requirements)


def _read(file_path):
    with file(file_path, 'r') as infile:
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
    install_requires=_get_requirements('requirements/prod.txt'),
    long_description=_read('README.rst'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
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
        'm3-builder>=1.0.1',
    ),
    set_build_info=dirname(__file__),
)
