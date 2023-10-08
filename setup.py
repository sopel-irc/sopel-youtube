# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
from setuptools import setup, find_packages


if __name__ == '__main__':
    print('Sopel does not correctly load plugins installed with setup.py '
          'directly. Please use "pip install .", or add '
          '{}/sopel_youtube to core.extra in your config.'
          .format(os.path.dirname(os.path.abspath(__file__))),
          file=sys.stderr)

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('NEWS') as history_file:
    history = history_file.read()


setup(
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
)
