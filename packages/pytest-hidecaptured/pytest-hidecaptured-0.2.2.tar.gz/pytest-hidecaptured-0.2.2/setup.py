#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-hidecaptured",
    version="0.2.2",
    author="Hamza Sheikh",
    author_email="code@codeghar.com",
    maintainer="Hamza Sheikh",
    maintainer_email="code@codeghar.com",
    license="MIT",
    url="https://github.com/codeghar/pytest-hidecaptured",
    description="Hide captured output",
    long_description=read("README.md"),
    py_modules=["pytest_hidecaptured"],
    install_requires=["pytest>=2.8.5"],
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"pytest11": ["hidecaptured = pytest_hidecaptured"]},
)
