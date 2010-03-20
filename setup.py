import glob, sys
from distutils.core import setup
try:
    from setuptools import setup
except ImportError:
    pass

version = '0.4'

setup(name="template2pdf",
      version=version,
      description=("Generates PDF via trml2pdf using template engine(s): \n"
                   "Superceding django_trml2pdf."),
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Yasushi Masuda, Accense Technology, Inc.",
      author_email="ymasuda at accense.com or whosaysni at gmail.com",
      url="http://code.google.com/p/template2pdf/",
      license="LGPL",
      zip_safe=False,
      packages=["template2pdf", "template2pdf.dj",
                "template2pdf/dj/templatetags"],
      data_files=[[dirname, glob.glob(dirname+'/*')]
                  for dirname in ["template2pdf/dj/templates",
                                  "template2pdf/dj/resources",]],
      test_suite = 'tests.suite',
      )
