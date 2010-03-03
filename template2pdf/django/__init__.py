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

"""PDF renderer, using trml2pdf
"""
import os.path
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.html import escape

from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily

from trml2pdf import trml2pdf
trml2pdf.encoding = 'utf-8'

# Refer to django.conf settings for PDF_RESOURCES and PRELOAD_FONTS.
try:
    PDF_RESOURCES = settings.TRML2PDF_RESOURCES
except:
    # PDF_RESOURCES defaults to './resources'.
    PDF_RESOURCES = [os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'resources')]
try:
    PRELOAD_FONTS = settings.TRML2PDF_PRELOAD_FONTS
    # PRELOAD_FONTS defaults to empty list.
except:
    PRELOAD_FONTS = []
    # 
    # PRELOAD_FONTS, if specified, should be a list of font registry.
    # - Each registry should be a tuple of (font-family-name, font-info).
    #   - Font-info should be a list of font parameters.
    #   - Each parameter is a tuple of (type, fontname, filename, params).
    #     - Type should be 'UnicodeCIDFont' or 'TTFont'.
    #     - Fontname is the font name used in rml documents.
    #     - For TTFont, filename should be supplied, as relative path
    #       to resource directory.
    #     - Params is a dictionary to be passed into font constructor.
    # - Setting non-null font-family-name will registar font family.
    #
    # Here is a sample PRELOAD_FONTS declaration for Japanese documents.
    # TRML2PDF_PRELOAD_FONTS = [
    #     (None, [('UnicodeCIDFont', 'HeiseiKakuGo-W5', None, None)]),
    #     (None, [('UnicodeCIDFont', 'HeiseiMin-W3', None, None)]),
    #     ('IPA Mincho', [('TTFont', 'IPA Mincho', 'fonts/ipam.ttf', None),
    #                     ('TTFont', 'IPA Mincho', 'fonts/ipam.ttf', None),
    #                     ('TTFont', 'IPA Mincho', 'fonts/ipam.ttf', None),
    #                     ('TTFont', 'IPA Mincho', 'fonts/ipam.ttf', None),]),
    #     (None, [('TTFont', 'IPA Gothic', 'fonts/ipag.ttf', None)]),
    #     (None, [('TTFont', 'IPA PMincho', 'fonts/ipapm.ttf', None)]),
    #     (None, [('TTFont', 'IPA PGothic', 'fonts/ipapg.ttf', None)]), ]


def find_resource_abspath(path):
    """Find file resource from PDF_RESOURCES and return the absolute path.
    """
    for resource_dir in PDF_RESOURCES:
        try_path = os.path.join(resource_dir, path)
        if os.path.exists(try_path):
            return os.path.abspath(try_path)
    return None


def load_font(font_type, font_name, font_path, params=None):
    """Load a font.
    """
    if font_type=='UnicodeCIDFont':
        return UnicodeCIDFont(font_name)
    elif font_type=='TTFont':
        font_abspath = find_resource_abspath(font_path)
        if font_abspath:
            params = params or {}
            return TTFont(font_name, font_abspath, **params)
    return None


def initialize():
    """Register font (and font family) according to PRLOAD_FONTS.
    """
    for family, fonts_info in PRELOAD_FONTS:
        faces = []
        for font_info in fonts_info:
            font = load_font(*font_info)
            if font:
                registerFont(font)
                faces.append(font_info[1])
        if family and faces:
            registerFontFamily(family, *faces)
    return True


# Initialize once on loading module.
try:
    initialized_
except:
    initialized_ = initialize()


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


def rml2pdf(rml):
    """Generates CJK-aware PDF using monkeypatched trml2pdf.
    """
    doc = rml_doc_plus(rml)
    buf = StringIO()
    doc.render(buf)
    return buf.getvalue()


def direct_to_pdf(
    request, template_name, params=None, context_object=None,
    pdf_name=None, download=True):
    """Renders PDF from RML, which is rendered from a Django template.

    >>> from django.http import HttpRequest
    >>> resp = direct_to_pdf(HttpRequest(), 'common/base.rml')
    >>> resp['content-type'], resp['content-disposition']
    ('application/pdf', 'attachment; filename=base.pdf')
    >>> resp.content[:8]
    '%PDF-1.4'
    """
    context_object = context_object or RequestContext(request)
    params = params or {}
    pdf_name = pdf_name or params.pop('pdf_name', None)
    if pdf_name==None:
        tname_body = template_name.rpartition('/')[-1].rpartition('.')[0]
        if tname_body:
            pdf_name = tname_body+'.pdf'
        else:
            pdf_name = 'download.pdf'
    params['pdf_name'] = pdf_name
    rml = render_to_string(
        template_name, params, context_object).encode('utf-8')
    try:
        pdf = rml2pdf(rml)
    except Exception, e:
        rml = escape(rml)
        raise TemplateSyntaxError(str(e))
    response = HttpResponse(pdf, mimetype='application/pdf')
    if download:
        response['Content-Disposition'] = (
            'attachment; filename=%s' %(pdf_name))
    return response
