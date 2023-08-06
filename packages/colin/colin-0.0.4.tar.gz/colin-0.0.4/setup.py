#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup

BASE_PATH = os.path.dirname(__file__)

# https://packaging.python.org/guides/single-sourcing-package-version/
version = {}
with open("./colin/version.py") as fp:
    exec(fp.read(), version)

long_description = ''.join(open('README.md').readlines())

setup(
    name='colin',
    version=version["__version__"],
    description="Tool to check generic rules/best-practices for containers/images/dockerfiles.",
    long_description=long_description,
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=[
        'Click',
        'six',
        'conu>=0.3.0rc0',
        'dockerfile_parse'
    ],
    entry_points='''
        [console_scripts]
        colin=colin.cli.colin:cli
    ''',
    data_files=[("share/colin/rulesets/", ["rulesets/default.json",
                                           "rulesets/fedora.json"]),
                ("share/bash-completion/completions/", ["bash-complete/colin"])],
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
    ],
    keywords='containers,sanity,linter',
    author='Red Hat',
    author_email='flachman@redhat.com',
    url='https://github.com/user-cont/colin',
)
