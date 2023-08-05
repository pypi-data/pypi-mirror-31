#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

long_desc = '''Tools to automate projects in DjangoFramework'''

version = '0.2.0'

setup(name='alfred-tools',
  version=version,
  description='Tools to automate projects in DjangoFramework',
  long_description=long_desc,
  url='http://github.com/kevinzeladacl/alfred-tools',
  author='Kevinzeladacl',
  author_email='iam@kevinzeladacl.cl',
  maintainer='Kevinzeladacl',
  maintainer_email='iam@kevinzeladacl.cl',
  license='MIT',
  keywords='Tools to automate projects Django Framework',
  zip_safe=False,
  packages = ('alfred-tools',
                 'alfred-tools.management',
                 'alfred-tools.management.commands'),
  package_data={'alfred-tools': 'alfred-tools'},
  classifiers=[
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
])

 