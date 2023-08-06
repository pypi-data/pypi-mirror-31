#! /usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

import os
import sys
from setuptools import setup, find_packages


def read(fname):
    if os.path.exists(fname.replace('.md', '.rst')):
        return open(os.path.join(os.path.dirname(__file__), fname.replace('.md', '.rst'))).read()
    else:
        try:
            import pypandoc
            rst = pypandoc.convert(os.path.join(os.path.dirname(__file__), fname), 'rst')
            with open('README.rst', 'w') as f:
                f.write(rst)
            return rst
        except (IOError, ImportError):
            return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pybo",
    version="0.1.3",  #edit version in __init__.py
    author="Esukhia development team",
    author_email="esukhiadev@gmail.com",
    description="Python utils for processing Tibetan",
    license="Apache2",
    keywords="nlp computational_linguistics search ngrams language_models linguistics toolkit tibetan",
    url="https://github.com/Esukhia/pybo",
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    project_urls={
        'Source': 'https://github.com/Esukhia/pybo',
        'Tracker': 'https://github.com/Esukhia/pybo/issues',
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Text Processing :: Linguistic",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Tibetan"
    ],
    package_data={'pybo': ['resources/*', 'resources/trie/*']},
    python_requires='>=3',
)
