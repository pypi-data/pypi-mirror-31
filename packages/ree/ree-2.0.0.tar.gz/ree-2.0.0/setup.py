#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

packages = find_packages(exclude=["tests.*", "tests"])

setup(
    name='ree',
    version='2.0.0',
    description='Red Eléctrica de España data',
    license='MIT',
    long_description=long_description,
    url='https://github.com/blackleg/ree',
    author='blackleg',
    author_email='hectorespertpardo@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],
    packages=packages,
    install_requires=[
        'arrow',
        'requests'
    ]
)
