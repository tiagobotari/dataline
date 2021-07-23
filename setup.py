#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup, find_packages

INSTALL_REQUIRES = []

if __name__ == "__main__":
    setup(name='Dataline',
        version='0.0'
        , author=''
        , author_email='tiagobotari@gmail.com'
        , description="Simple class to aid the process of data cleaning."
        , license='https://github.com/tiagobotari/dataline'
        , url="https://github.com/rcabdia/CWT"
        , packages=find_packages()
        , install_requires=INSTALL_REQUIRES
        , zip_safe=False
        , python_requires='>=3.6'
    )
