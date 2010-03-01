# coding: utf-8
# Copyright (c) 2010 Accense Technology, Inc. All rights reserved.
import datetime

from django import template
from django.template import resolve_variable

from django_trml2pdf import find_resource_abspath


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
        return find_resource_abspath(actual_path) or ''


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

