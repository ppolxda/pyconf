# -*- coding: utf-8 -*-
u"""
@create: 2017-03-09 15:15:05.

@author: asdfsdf

@desc:
"""
import os
import sys
import codecs
import shutil
from setuptools import setup, find_packages, findall


setup(
    name="pyopts",
    version="0.0.10",
    install_requires=[
        'six',
    ],
    packages=find_packages('.'),
    # package_data={
    #     'pyeosloop': datas,
    # },
    # entry_points={
    #     "console_scripts": [
    #         "pdbtools_json=pypplugins.protoc_gen_json:main",
    #     ]
    # },
    # scripts=bin_list_build(),
    python_requires=">=2.7",
    author="asdas",
    author_email="sa@sa.com",
    description="This is an pyopts Package",
    license="PSF",
    keywords="examples",
    # url="http://example.com/HelloWorld/",
)
