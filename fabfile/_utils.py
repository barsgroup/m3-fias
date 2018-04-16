# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from functools import wraps

from pip.commands.install import InstallCommand
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution


def get_dependent_packages(package_name):
    """Возвращает имена пакетов, от которых зависит указанный пакет.

    Учитываются каскадные зависимости, поэтому имена могут повторяться.

    :params str package_name: имя пакета.

    :rtype: generator
    """
    distribution = get_distribution(package_name)

    for requirement in distribution.requires():
        yield get_distribution(requirement.name).project_name
        for name in get_dependent_packages(requirement.name):
            yield name


def is_packages_installed(*names):
    """Возвращает True, если пакет с указанным именем установлен.

    :param str name: имя пакета.

    :rtype: bool
    """
    for name in names:
        try:
            get_distribution(name)
        except DistributionNotFound:
            return False

    return True


def install_packages(*names):
    """Устанавливает пакеты с указанными именами.

    .. code-block: python

       install_packages('fabric3>=1', 'pip>9', 'django>=1.11,<2')
    """
    if names:
        cmd = InstallCommand()
        params = ['--quiet']
        params.extend(names)
        if cmd.main(params) != 0:
            raise RuntimeError('Package install failed: ' + ', '.join(names))


def install_requirements(requirements_file, quiet):
    """Проверяет наличие пакета и при отсутствии устанавливает пакеты из файла.

    :param unicode requirements_file: файл со списком зависимостей.
    """
    params = ['-r', requirements_file]
    if quiet:
        params.append('--quiet')

    cmd = InstallCommand()
    if cmd.main(params) != 0:
        raise RuntimeError(
            'Package install failed: ' + requirements_file
        )


def require(*packages):
    """Декоратор, устанавливающий указанные пакеты, перед запуском функции."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            non_installed_packages = [
                package
                for package in packages
                if not is_packages_installed(package)
            ]
            if non_installed_packages:
                install_packages(*non_installed_packages)

            return func(*args, **kwargs)

        return wrapper

    return decorator


CODING_HEADER = '# coding: utf-8\n'


def _is_coding_header(header):
    return (
        header.startswith('#') and
        not header.startswith('#!') and
        'coding' in header.lower()
    )


def get_coding_declaration(file_path):
    """Возвращает информацию об объявлении кодировки python-модуля.

    :param str file_path: путь к файлу.

    :returns: кортеж из двух элементов:

      # ``True`` --- кодировка файла указана верно и соответствует
        ``CODING_HEADER``, ``False`` --- кодировка указана, но отличается от
        ``CODING_HEADER``, ``None`` --- кодировка не указана.
      # ``None``, либо строка загоровка, если он указан и отличается от
        ``CODING_HEADER``.
    """
    assert file_path.endswith('.py'), file_path

    with open(file_path, 'r') as python_file:
        header = python_file.readline()

    if _is_coding_header(header):
        if header == CODING_HEADER:
            result = True, None
        else:
            result = False, header
    else:
        result = None, None

    return result


def fix_file_coding(file_path):
    """Исправляет объявление кодировки в python-модуле.

    Если кодировка в файле указана, но не соответствует ``CODING_HEADER``, то
    заменяет её объявление на ``CODING_HEADER``.

    :param str file_path: путь к файлу.
    """
    assert file_path.endswith('.py'), file_path

    with open(file_path, 'r') as f:
        header = f.readline()
        content = f.read()

    if _is_coding_header(header):
        if header == CODING_HEADER:
            header = None
        else:
            header = CODING_HEADER
    else:
        if header.startswith('#!'):
            header = None
        else:
            content = header + content
            header = CODING_HEADER

    if header is not None:
        with open(file_path, 'w') as f:
            f.write(header)
            f.write(content)
