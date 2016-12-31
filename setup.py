#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend(
            [os.path.join(base, filename) for filename in filenames])
    return {package: filepaths}


version = get_version('ifparser')

with open('README.rst') as f:
    long_description = '\n\n'.join(f.read().split('\n\n')[1:])

setup(
    name='ifparser',
    version=version,
    url='http://github.com/tripples/ifconfig-parser',
    download_url='http://github.com/tripples/ifconfig-parser',
    license='BSD',
    description='Parse ifconfig output and retrieve values with goodies',
    long_description=long_description,
    author='Sanket Sudake',
    author_email='sanketsudake@gmail.com',
    packages=get_packages('ifparser'),
    package_data=get_package_data('ifparser'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries"
    ], )
