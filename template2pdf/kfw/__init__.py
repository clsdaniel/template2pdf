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

import kay
from kay.conf import settings
from kay.utils import local, render_to_string

try:
    import urllib
    urllib.getproxies_macosx_sysconf = lambda : {}
except:
    pass

# DIRTY HACK: Hard to explain why this works... :(
try:
    import reportlab.lib.utils
    from google.appengine.api import images
    reportlab.lib.utils.Image = images.Image
    reportlab.lib.utils.hasImage = True
    reportlab.lib.utils._isPILImage = lambda im: True
except:
    pass
try:    
    import os.path
    # os.path.expanduser = lambda p: p.replace('~', '')
    from google.appengine.tools.dev_appserver import HardenedModulesHook as _H
    _H._files = {}
    _H._WHITE_LIST_C_MODULES.append('_ctypes')
    del _H
except:
    pass


from template2pdf.utils import find_resource_path, find_resource_abspath, rml2pdf, FontResolver


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
    from os.path import abspath, dirname
    rootdir = dirname(dirname(abspath(kay.__file__)))
    dirs = None or []
    for dir_ in dirs+[path.replace('.', '/')
                      for path in settings.INSTALLED_APPS]:
        path = os.path.join(rootdir, dir_, resource_dirname)
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

font_resolver = FontResolver(FONT_DIRS, FONT_CACHE).resolve_font

# def font_resolver(font_type, params):
#     """Default TTF font resolver.
#     """
#     if font_type=='UnicodeCIDFont':
#         faceName = params.get('faceName', '')
#         font = UnicodeCIDFont(faceName)
#         return font
#     elif not (font_type=='TTFont'):
#         return None
#     faceName = params.get('faceName', '')
#     fileName = find_resource_abspath(params.get('fileName', ''), FONT_DIRS)
#     if not (faceName and fileName):
#         return
#     subfontIndex = int(params.get('subfontIndex', '0'))
#     key = (fileName, subfontIndex)
#     if key in FONT_CACHE.keys():
#         return FONT_CACHE[key]
#     from reportlab.pdfbase.ttfonts import TTFont
#     font = TTFont(faceName, fileName, subfontIndex=subfontIndex)
#     if font:
#         FONT_CACHE[key] = font
#     return font

def image_resolver(node):
    fname = find_resource_path(str(node.getAttribute('file')), RESOURCE_DIRS)
    from google.appengine.api.images import Image
    from template2pdf.t2p.utils import as_pt
    img = Image(file(fname, 'rb').read())
    sx, sy = img.width, img.height
    args = {}
    for tag in ('width', 'height', 'x', 'y'):
        if node.hasAttribute(tag):
            args[tag] = as_pt(node.getAttribute(tag))
    if ('width' in args) and (not 'height' in args):
        args['height'] = sy * args['width'] / sx
    elif ('height' in args) and (not 'width' in args):
        args['width'] = sx * args['height'] / sy
    elif ('width' in args) and ('height' in args):
        if (float(args['width'])/args['height'])>(float(sx)>sy):
            args['width'] = sx * args['height'] / sy
        else:
            args['height'] = sy * args['width'] / sx
    return fname, args


def pdf_resource(arg):
    if arg.startswith('/'):
        return arg.lstrip('/')
    else:
        return find_resource_path(arg, RESOURCE_DIRS)


def render_to_pdf(template_name, params,
                  font_resolver=font_resolver,
                  image_resolver=image_resolver):
    """Renders PDF from RML, which is rendered from a Django template.
    """
    rml = render_to_string(template_name, params).encode('utf-8')
    try:
        pdf = rml2pdf(rml, font_resolver, image_resolver)
    except Exception, e:
        raise TemplateError(str(e))
    return pdf


def direct_to_pdf(request, template_name, params=None,
                  pdf_name=None, download=False,
                  font_resolver=font_resolver,
                  image_resolver=image_resolver):
    """Simple generic view to tender rml template.
    """
    params = params or {}
    params['pdf_resource'] = pdf_resource
    pdf_name = pdf_name or params.pop('pdf_name', None)
    if pdf_name==None:
        tname_body = template_name.rpartition('/')[-1].rpartition('.')[0]
        if tname_body:
            pdf_name = tname_body+'.pdf'
        else:
            pdf_name = 'download.pdf'
    params['pdf_name'] = pdf_name
    pdf = render_to_pdf(template_name, params,
                        font_resolver=font_resolver,
                        image_resolver=image_resolver)
    response = Response(pdf, mimetype='application/pdf')
    if download:
        disposition = 'attachment; filename=%s' %(pdf_name)
        response.headers['Content-Disposition'] = disposition
    return response
