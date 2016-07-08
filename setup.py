# coding: utf-8
import os

from pip.download import PipSession
from pip.req.req_file import parse_requirements
from setuptools import setup, find_packages


def _get_requirements(file_name):
    pip_session = PipSession()
    requirements = parse_requirements(file_name, session=pip_session)

    return tuple(str(requirement.req) for requirement in requirements)


def _read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__),
            fname)).read()
    except IOError:
        return ''


setup(
    name='m3-fias',
    url='https://bitbucket.org/barsgroup/m3-fias',
    license='MIT',
    author='BARS Group',
    description=u'Федеральная информационная адресная система',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=_get_requirements('requirements.txt'),
    long_description=_read('README.rst'),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.0.1',
    ),
    set_build_info=os.path.dirname(__file__),
)
