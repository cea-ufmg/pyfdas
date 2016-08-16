#!/usr/bin/env python3

from setuptools import setup, find_packages

DESCRIPTION = open("README.rst", encoding="utf-8").read()

CLASSIFIERS = '''\
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved
Operating System :: POSIX
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3 :: Only
Topic :: Scientific/Engineering'''

setup(
    name="pyfdas",
    version="0.1.dev1",
    packages=find_packages(),
    install_requires=[],
    tests_require=["pytest"],
    
    # metadata for upload to PyPI
    author="Dimas Abreu Dutra",
    author_email="dimasadutra@gmail.com",
    description='CEA Flight Data Acquisition System.',
    classifiers=CLASSIFIERS.split('\n'),
    platforms=["Linux", "Unix"],
    license="MIT",
    url="http://github.com/cea-ufmg/ceacoest",
)
