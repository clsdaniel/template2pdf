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

from t2p import trml2pdf

# caches pre-loaded fonts
FONT_CACHE = {}


def find_resource_path(path, resource_dirs, absolute=False):
    """Find resource file from resource_dirs and return its (absolute) path.

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
    """Wraps find_resource_path always to return absolute path.
    """
    return find_resource_path(path, resource_dirs, absolute=True)


def rml2pdf(rml, font_resolver=None, image_resolver=None):
    """Generates CJK-aware PDF using (a forked) trml2pdf.
    """
    doc = trml2pdf._rml_doc(rml, font_resolver, image_resolver)
    buf = StringIO()
    doc.render(buf)
    return buf.getvalue()


class FontResolver(object):
    """Default font resolver.
    """
    
    def __init__(self, font_dirs=None, font_cache=None):
        """Remember font_dirs/font_cache.
        """
        self.font_dirs = font_dirs
        self.font_cache = font_cache

    def resolve_font(self, font_type, params):
        """Resolves font for given font_type and parms.
        """
        if font_type=='UnicodeCIDFont':
            font = self.resolve_cidfont(params)
        elif font_type=='TTFont':
            font = self.resolve_ttfont(params)
        return font
    
    def resolve_cidfont(self, params):
        """Resolves CIDFont.
        """
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        faceName = params.get('faceName', '')
        key = (faceName, )
        if key in self.font_cache:
            font= self.font_cache.get(key)
        else:
            font = self.font_cache.setdefault(key, UnicodeCIDFont(faceName))
        return font

    def resolve_ttfont(self, params):
        """Resolves TTFont (and put it in cache).
        """
        from reportlab.pdfbase.ttfonts import TTFont
        faceName = params.get('faceName', '')
        fileName = params.get('fileName', '')
        if not fileName.startswith('/'):
            fileName = find_resource_abspath(fileName, FONT_DIRS)
        subfontIndex = int(params.get('subfontIndes', '0'))
        key = (faceName, fileName, subfontIndex)
        if key in self.font_cache:
            font= self.font_cache.get(key)
        else:
            font = self.font_cache.setdefault(
                key, TTFont(faceName, fileName, False, subfontIndex))
        return font

if __name__=="__main__":
    from doctest import testmod
    testmod()
