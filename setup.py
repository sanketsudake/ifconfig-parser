#!/usr/bin/env python
# -*- coding: utf-8 -*-
from package_utils import (get_version, get_packages, get_package_data)
from setuptools import setup

version = get_version('ifparser')

with open('README.rst') as f:
    long_description = '\n\n'.join(f.read().split('\n\n')[1:])

setup(
    name='ifparser',
    version=version,
    url='http://github.com/tripples/ifconfig-parser',
    download_url='http://github.com/tripples/ifconfig-parser',
    license='BSD',
    description='Parse ifconfig output and retrieve values',
    long_description=long_description,
    author='Sanket Sudake',
    author_email='sanketsudake@gmail.com',
    packages=get_packages('ifparser'),
    package_data=get_package_data('ifparser'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
)
