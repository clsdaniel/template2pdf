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
from trml2pdf import trml2pdf
trml2pdf.encoding = 'utf-8'

# caches pre-loaded fonts
FONT_CACHE = {}


def find_resource_path(path, resource_dirs, absolute=False):
    """Find resource file from resource_dirs and return its absolute path.
    """
    for resource_dir in resource_dirs:
        try_path = os.path.join(resource_dir, path)
        if os.path.exists(try_path):
            if absolute:
                return os.path.abspath(try_path)
            return try_path
    raise ValueError("Unable to find resource '%s', tried: %s" %(path, resource_dirs))

def find_resource_abspath(path, resource_dirs):
    return find_resource_path(path, resource_drs, absolute=True)

class rml_styles_plus(trml2pdf._rml_styles):
    """This is a hack of _rml_styles to support CJK wordWrap.
    """
    def _para_style_update(self, style, node):
        """Extended _rml_styles._para_style_update to support wordWrap.
        """
        style = super(rml_styles_plus, self)._para_style_update(style, node)
        for attr in ['wordWrap']:
            if node.hasAttribute(attr):
                style.__dict__[attr] = node.getAttribute(attr)
        return style
    

class rml_doc_plus(trml2pdf._rml_doc):
    """_rml_doc using rml_styles_plus instead to support CJK document.
    """
    def __init__(self, data, font_resolver=None):
        """Extends _rml_doc so that font_resolver attribute is supported.
        """
        super(rml_doc_plus, self).__init__(data)
        self.font_resolver = font_resolver

    def docinit(self, els):
        """Registers both UnicodeCIDFonts and TTFonts.
        """
        for node in els:
            # register CID fonts
            for subnode in node.getElementsByTagName('registerCidFont'):
                faceName = subnode.getAttribute('faceName').encode('utf-8')
                font = UnicodeCIDFont(faceName)
                if font:
                    registerFont(font)
            # register TrueType fonts
            for subnode in node.getElementsByTagName('registerTTFont'):
                faceName = subnode.getAttribute('faceName').encode('utf-8')
                fileName = subnode.getAttribute('fileName').encode('utf-8')
                subfontIndex = subnode.getAttribute('subfontIndex')
                if subfontIndex:
                    subfontIndex = int(subfontIndex)
                else:
                    subfontIndex = 0
                if self.font_resolver:
                    params = dict(faceName=faceName,
                                  fileName=fileName,
                                  subfontIndex=subfontIndex)
                    # Resolver is recommended to implement cache.
                    font = self.font_resolver('TTFont', params)
                else:
                    # Built-in cache.
                    font = FONT_CACHE.setdefault(
                        (faceName, fileName),
                        TTFont(faceName, fileName, False, subfontIndex))
                if font:
                    registerFont(font)

    def render(self, out):
        """Renders document, retriving styles with rml_styles_plus().
        """
        el = self.dom.documentElement.getElementsByTagName('docinit')
        if el:
            self.docinit(el)
        el = self.dom.documentElement.getElementsByTagName('stylesheet')
        self.styles = rml_styles_plus(el)
        el = self.dom.documentElement.getElementsByTagName('template')
        if len(el):
            pt_obj = trml2pdf._rml_template(out, el[0], self)
            pt_obj.render(self.dom.documentElement.getElementsByTagName('story')[0])
        else:
            self.canvas = canvas.Canvas(out)
            pd = self.dom.documentElement.getElementsByTagName('pageDrawing')[0]
            pd_obj = trml2pdf._rml_canvas(self.canvas, None, self)
            pd_obj.render(pd)
            self.canvas.showPage()
            self.canvas.save()


def rml2pdf(rml, font_resolver=None):
    """Generates CJK-aware PDF using monkeypatched trml2pdf.
    """
    doc = rml_doc_plus(rml, font_resolver)
    buf = StringIO()
    doc.render(buf)
    return buf.getvalue()
