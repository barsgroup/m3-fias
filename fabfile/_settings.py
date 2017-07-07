# coding: utf-8
from os.path import abspath
from os.path import dirname
from os.path import join


#: Имя пакета с проектом.
PROJECT_PACKAGE = 'm3_fias'


#: Папка проекта.
PROJECT_DIR = dirname(dirname(abspath(__file__)))


#: Папка с исходными кода проекта.
SRC_DIR = join(PROJECT_DIR, 'src')


#: Папка с документацией.
DOCS_DIR = join(PROJECT_DIR, 'docs')


#: Папка со списками зависимостей проекта.
REQUIREMENTS_DIR = join(PROJECT_DIR, 'requirements')


#: Путь к файлу со списком зависимостей проекта для production-среды.
REQUIREMENTS_PROD = join(REQUIREMENTS_DIR, 'prod.txt')


#: Путь к файлу со списком зависимостей проекта для development-среды.
REQUIREMENTS_DEV = join(REQUIREMENTS_DIR, 'dev.txt')
