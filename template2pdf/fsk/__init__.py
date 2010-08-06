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

"""PDF renderer, using trml2pdf, for flask-framework
"""
import os.path
from jinja2 import contextfunction, Template, TemplateError
from werkzeug import escape, Response
from flask import Module, request
from template2pdf.utils import FontResolver, find_resource_path, find_resource_abspath, rml2pdf

# make this as a module
mod = Module(__name__)

FONT_DIRS = []
RESOURCE_DIRS = []
# populate RESOURCE_DIR with 'resources' under project and application dirs
def populate_resource_dirs(dirs=None, resource_dirname='resources'):
    from os.path import abspath, dirname
    rootdir = dirname(dirname(abspath(__file__)))
    dirs = None or []
    for dir_ in dirs:
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
        raise
        raise TemplateError(str(e))
    return pdf

def render_to_string(template, context={}, processors=None):
  """
  A function for template rendering adding useful variables to context
  automatically, according to the CONTEXT_PROCESSORS settings.
  """
  if processors is None:
    processors = ()
  else:
    processors = tuple(processors)
  for processor in processors:
    context.update(processor(request))
  template = Template(mod.open_resource('templates/%s' %(template)).read())
  return template.render(context)


def direct_to_pdf(template_name, params=None,
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
