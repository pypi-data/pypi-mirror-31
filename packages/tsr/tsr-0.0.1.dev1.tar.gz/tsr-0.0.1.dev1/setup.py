#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools, os, sys
from distutils.core import setup

setup(
        name = 'tsr',
        version = '0.0.1.dev1',
        description = 'TSR on command-line',
        author = 'Methmo',
        author_email = 'adammarkgray@gmail.com',
        license='MIT',
        url = 'https://github.com/methmo/tsr',
        download_url = 'https://gitlab.com/methmo/tsr/archive/0.0.1.dev1.tar.gz',
        classifiers = [
            'Development Status :: 1 - Planning',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows :: Windows 10',
            'Operating System :: Microsoft :: Windows :: Windows 7',
            'Operating System :: Microsoft :: Windows :: Windows 8',
            'Operating System :: Microsoft :: Windows :: Windows 8.1',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Terminals',
            'Topic :: Text Processing'
        ],
        keywords = 'tsr student forum command line cli cl scraper',
        packages = setuptools.find_packages(),
        install_requires = [
            'beautifulsoup4>=4.6.0',
            'colorama>=0.3.9',
            'simplejson>=3.12.0',
            'matplotlib>=2.1.1',
            'pandas>=0.20.3',
            'requests>=2.18.1'
        ],
        python_requires='>=3.5, <4',
        include_package_data=True,
        entry_points={
            'console_scripts': [
                'tsr = tsr.tsr_on_cl:main'
            ]
        }
)
