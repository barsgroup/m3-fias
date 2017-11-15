# coding: utf-8


class AssertionError(__builtins__['AssertionError']):

    __doc__ = __builtins__['AssertionError'].__doc__

    def __init__(self, message='', *args, **kwargs):
        u"""Кодирует unicode сообщение в utf-8."""
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        super(AssertionError, self).__init__(message, *args, **kwargs)


def patch_utf8_assertion_error():
    u"""Кодирует сообщения AssertionError в utf-8.

    Т.к. обычно используемая кодировка в терминале utf-8, а python по
    какой-то причине не кодирует сообщения в кодировку stderr, то сообщения
    исключений выводятся в виде кодов символов.

    Чтобы избежать этого, мы принудительно конвертируем unicode строки
    в utf-8.
    """
    __builtins__['AssertionError'] = AssertionError
