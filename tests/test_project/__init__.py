# coding: utf-8
from __future__ import absolute_import

import sys


if sys.version_info.major == 2:
    from .patches import patch_utf8_assertion_error

    patch_utf8_assertion_error()
