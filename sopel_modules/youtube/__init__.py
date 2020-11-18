# coding=utf8
"""sopel-youtube

YouTube plugin for Sopel
"""
from __future__ import unicode_literals, absolute_import, division, print_function

try:
    from .youtube import *
except ImportError:
    # probably being imported by setup.py to get metadata before installation
    # no cause for alarm
    pass

__author__ = 'dgw'
__email__ = 'dgw@technobabbl.es'
__version__ = '0.4.0'

