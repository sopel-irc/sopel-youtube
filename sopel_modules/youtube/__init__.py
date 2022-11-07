# coding=utf8
"""sopel-youtube

YouTube plugin for Sopel
"""
from __future__ import unicode_literals, absolute_import, division, print_function

# replace with `importlib_metadata` when updating for Sopel 8.0
import pkg_resources

from .youtube import *

__author__ = 'dgw'
__email__ = 'dgw@technobabbl.es'
__version__ = pkg_resources.get_distribution('sopel_modules.youtube').version
