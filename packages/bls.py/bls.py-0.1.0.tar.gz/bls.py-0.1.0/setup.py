#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, Extension


def get_extensions():
    import numpy
    from Cython.Build import cythonize
    ext = Extension(
        "bls._impl",
        sources=[
            os.path.join("bls", "bls.c"),
            os.path.join("bls", "_impl.pyx"),
        ],
        include_dirs=[numpy.get_include()],
    )
    return cythonize([ext])


setup(
    name="bls.py",
    version="0.1.0",
    author="Daniel Foreman-Mackey & Ze Vinicius",
    author_email="foreman.mackey@gmail.com",
    url="https://github.com/dfm/bls.py",
    license="BSD",
    packages=["bls"],
    ext_modules=get_extensions(),
    setup_require=["numpy", "cython"],
)
