# coding: utf-8
# Copyright (c) 2010 Accense Technology, Inc. All rights reserved.

import glob, sys
from distutils.core import setup
try:
    from setuptools import setup
except ImportError:
    pass


version = '0.5'

setup(
    name="template2pdf",
    version=version,
    description=("Renders Django/Jinja2 templates into PDF."),
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                 "Programming Language :: Python",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    author="Yasushi Masuda, Accense Technology, Inc.",
    author_email="ymasuda at accense.com or whosaysni at gmail.com",
    url="http://code.google.com/p/template2pdf/",
    license="LGPL",
    zip_safe=True,
    packages=["template2pdf", "template2pdf.t2p", "template2pdf.dj",
              "template2pdf/dj/templatetags", "template2pdf.kfw",],
    data_files=([[dirname, glob.glob(dirname+'/*')]
                 for dirname in ["template2pdf/dj/templates",
                                 "template2pdf/dj/resources",
                                 "template2pdf/kfw/templates",
                                 "template2pdf/kfw/resources"]]+
                [['template2pdf/t2p', glob.glob('template2pdf/t2p/*.txt')]]),
    test_suite = 'tests.suite')
