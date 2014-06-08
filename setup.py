#coding: utf-8
from setuptools import setup, find_packages

requires = []
with open('requirements.txt', 'r') as f:
    requires.extend(f.readlines())

setup(name='m3-fias',
      version='0.1.1.0',
      url='https://src.bars-open.ru/py/m3/m3_contrib/kladr',
      license='Apache License, Version 2.0',
      author='BARS Group',
      description=u'Федеральная информационная адресная система',
      author_email='telepenin@bars-open.ru',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=requires,
      include_package_data=True,
      classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
