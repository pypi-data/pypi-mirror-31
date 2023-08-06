#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup file, used to install and test 'compressed_rtf'
"""

import os
from compressed_rtf import __version__
from setuptools import setup


with open('README.md') as file:
    long_description = file.read()

setup(
    name='compressed_rtf',
    version=__version__,
    author='Dmitry Alimov',
    description='Compressed Rich Text Format (RTF) compression and decompression package',
    long_description=long_description,
    license='MIT',
    keywords='compressed-rtf lzfu mela rtf',
    url='https://github.com/delimitry/compressed_rtf',
    packages=['compressed_rtf'],
    test_suite='tests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing',
        'Topic :: System :: Archiving :: Compression',
    ],
)