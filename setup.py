import sys
from distutils.core import setup
try:
    from setuptools import setup
except ImportError:
    pass

version = '0.1'

setup(name="django_trml2pdf",
      version=version,
      description="Generates PDF via trml2pdf from django application",
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Yasushi Masuda, Accense Technology, Inc.",
      author_email="whosaysni@gmail.com",
      url="http://code.google.com/p/trml2pdf/",
      license="LGPL",
      zip_safe=False,
      packages=["django_trml2pdf", "django_trml2pdf/templatetags"],
      package_data={"django_trml2pdf/templates/trml2pdf": "*",
                    "django_trml2pdf/resources": "*",},
      )
