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

import datetime

from django import template
from django.conf import settings
from django.template import resolve_variable

from template2pdf.django import find_resource_abspath, RESOURCE_DIRS


register = template.Library()


class PdfResourceNode(template.Node):
    """Node for {% pdf_resource resname %} tag.

    Resname can be quoted string or bare string, where former will
    be treated as a literal string, latter as a context variable.
    """
    def __init__(self, path):
        self.path = path

    def render(self, context):
        """Finds resource absolute path and render.
        """
        if ((self.path.startswith('"') or self.path.startswith("'")) and
            (self.path.endswith('"') or self.path.endswith("'"))):
            actual_path = self.path[1:-1]
        else:
            try:
                actual_path = resolve_variable(self.path, context)
            except template.VariableDoesNotExist:
                return ''
        return find_resource_abspath(actual_path, RESOURCE_DIRS) or ''


@register.tag
def pdf_resource(parser, token):
    """Generates PdfResourceNode for {% pdf_resource %} tag.
    """
    try:
        tag_name, path = token.split_contents()
    except ValueError:
        raise (template.TemplateSyntaxError,
               "%r tag requires exactly one argument"
               % token.contents.split()[0])
    return PdfResourceNode(path)

