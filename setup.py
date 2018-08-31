#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="fixedfieldreader",
    version="0.9.0",
    packages=find_packages(),
    description="Reader for lines with fixed-width fields",
    long_description="""This module provides classes to read and split files whose lines contain fixed-width fields, such as the FHFA PUDB or CDC WONDER mortality datasets.""",
    license="Apache Software License 2.0",
    keywords="fixed-width file-format reader",
    url="https://github.com/nkrishnaswami/fixed-field-reader",

    test_suite='nose.collector',
    tests_require=['nose'],

    install_requires=[
    ],

    author="Natarajan Krishnaswami",
    author_email="nkrish@acm.org",
    classifiers=[
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
