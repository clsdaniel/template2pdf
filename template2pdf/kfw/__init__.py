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

"""PDF renderer, using trml2pdf, for kay-framework
"""
import os.path

from jinja2 import contextfunction, TemplateError
from werkzeug import escape, Response

from kay.conf import settings
from kay.utils import render_to_string

try:
    from google.appengine.tools.dev_appserver import HardenedModulesHook as _H
    _H._files = {}
    del _H
except:
    pass
from template2pdf.utils import find_resource_abspath, rml2pdf


# values from settings
try:
    FONT_DIRS = settings.T2P_FONT_DIRS
except:
    FONT_DIRS = []
try:
    RESOURCE_DIRS = settings.T2P_RESOURCE_DIRS
except:
    RESOURCE_DIRS = []
# populate RESOURCE_DIR with 'resources' under project and application dirs
def populate_resource_dirs(dirs=None, resource_dirname='resources'):
    if dirs==None:
        dirs = [os.path.dirname(os.path.abspath(__file__))]
    for dir_ in dirs:
        path = os.path.join(dir_, resource_dirname)
        if (path not in RESOURCE_DIRS):
            RESOURCE_DIRS.append(path)
populate_resource_dirs()        

# populate FONT_DIRS with RESOURCE_DIRS/fonts
def populate_font_dirs(dirs=RESOURCE_DIRS, font_dirname='fonts'):
    prepends = []
    for dir_ in dirs:
        path = os.path.join(os.path.abspath(dir_), font_dirname)
        if (path not in FONT_DIRS):
            FONT_DIRS.append(path)
populate_font_dirs()        
# font cache
FONT_CACHE = {}


def font_resolver(font_type, params):
    """Default TTF font resolver.
    """
    if not (font_type=='TTFont'):
        return
    faceName = params.get('faceName', '')
    fileName = params.get('fileName', '')
    if not fileName.startswith('/'):
        fileName = find_resource_abspath(fileName, FONT_DIRS)
    if not (faceName and fileName):
        return
    subfontIndex = int(params.get('subfontIndex', '0'))
    key = (fileName, subfontIndex)
    if key in FONT_CACHE.keys():
        return FONT_CACHE[key]
    from reportlab.pdfbase.ttfonts import TTFont
    font = TTFont(faceName, fileName, subfontIndex=subfontIndex)
    if font:
        FONT_CACHE[key] = font
    return font


# This is a hack (and a scrap). subject to change
@contextfunction
def pdf_resource(context, arg):
    path = ''
    if arg:
        if not ((arg.startswith("'") or arg.startswith('"'))
                and (arg.endswith("'") or arg.endswith('"'))):
            path = context.get(arg)
        if not path.startswith('/'):
            path = find_resource_abspath(path, RESOURCE_DIRS)
        return path
    return
CONTEXT = dict(pdf_resource=pdf_resource)


def render_to_pdf(template_name, params, font_resolver=font_resolver):
    """Renders PDF from RML, which is rendered from a Django template.
    """
    params.update(CONTEXT)
    rml = render_to_string(template_name, params).encode('utf-8')
    try:
        pdf = rml2pdf(rml, font_resolver)
    except Exception, e:
        rml = escape(rml)
        raise TemplateError(str(e))
    return pdf


def direct_to_pdf(request, template_name, params=None,
                  pdf_name=None, download=False):
    """Simple generic view to tender rml template.
    """
    params = params or {}
    pdf_name = pdf_name or params.pop('pdf_name', None)
    if pdf_name==None:
        tname_body = template_name.rpartition('/')[-1].rpartition('.')[0]
        if tname_body:
            pdf_name = tname_body+'.pdf'
        else:
            pdf_name = 'download.pdf'
    params['pdf_name'] = pdf_name
    pdf = render_to_pdf(template_name, params)
    response = Response(pdf, mimetype='application/pdf')
    if download:
        disposition = 'attachment; filename=%s' %(pdf_name)
        response.headers['Content-Disposition'] = disposition
    return response
