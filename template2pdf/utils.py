# coding: utf-8

# Copyright (c) 2010 Accense Technology, Inc. All rights reserved.
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily

# A HACK -- force trml2pdf to expect utf-8 for templates
from t2p import trml2pdf

# caches pre-loaded fonts
FONT_CACHE = {}


def find_resource_path(path, resource_dirs, absolute=False):
    """Find resource file from resource_dirs and return its absolute path.

    >>> from os.path import abspath, dirname, join
    >>> thisdir = dirname(abspath(__file__))
    >>> found = find_resource_path('utils.py', [thisdir]) # should find
    >>> found == join(thisdir, 'utils.py')
    True
    >>> find_resource_path('nonexistent', [thisdir]) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: Unable to find resource 'nonexistent', tried: [...]
    """
    tried = []
    for resource_dir in resource_dirs:
        try_path = os.path.join(resource_dir, path)
        tried.append(os.path.abspath(try_path))
        if os.path.exists(try_path):
            if absolute:
                return os.path.abspath(try_path)
            return try_path
    raise ValueError("Unable to find resource '%s', tried: %s" %(path, tried))


def find_resource_abspath(path, resource_dirs):
    return find_resource_path(path, resource_dirs, absolute=True)


def rml2pdf(rml, font_resolver=None, image_resolver=None):
    """Generates CJK-aware PDF using monkeypatched trml2pdf.
    """
    doc = trml2pdf._rml_doc(rml, font_resolver, image_resolver)
    buf = StringIO()
    doc.render(buf)
    return buf.getvalue()


if __name__=="__main__":
    from doctest import testmod
    testmod()
