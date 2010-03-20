# coding: utf-8
# Copyright (c) 2010 Accense Technology, Inc. All rights reserved.
"""
"""
from os.path import abspath, dirname, join
from sys import path
path.insert(0, dirname(dirname(abspath(__file__))))
import unittest
import doctest

suite = unittest.TestSuite()

import template2pdf.utils
suite.addTests(doctest.DocTestSuite(template2pdf.utils))
