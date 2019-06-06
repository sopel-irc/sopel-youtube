# coding=utf8
"""Sopel YouTube Module

YouTube module for Sopel
"""
from __future__ import unicode_literals, absolute_import, division, print_function

try:
    from .youtube import *
except ImportError:
    # probably being imported by setup.py to get metadata before installation
    # no cause for alarm
    pass

__author__ = 'E. Powell'
__email__ = 'powell.518@gmail.com'
__version__ = '0.1.3'

