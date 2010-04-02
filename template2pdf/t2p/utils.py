# trml2pdf - An RML to PDF converter
# Copyright (C) 2003, Fabien Pinckaers, UCL, FSA
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

import re
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm


def as_bool(value):
    """Convert string into bool value.

    >>> as_bool('1'), as_bool('yes'), as_bool('YES')
    (True, True, True)
    >>> as_bool(''), as_bool('no'), as_bool('0')
    (False, False, False)
    >>> as_bool(None)
    Traceback (most recent call last):
    ...
    ValueError: Invalid argument: None
    """
    try:
        return (str(value)=="1") or (value.lower()=='yes')
    except:
        raise ValueError('Invalid argument: %s' %(value))
bool_get = as_bool # for backward compatibility: will be removed soon.


allcols = colors.getAllNamedColors()

regex_t = re.compile('\(([0-9\.]*),([0-9\.]*),([0-9\.]*)\)')
regex_h = re.compile('#([0-9a-zA-Z][0-9a-zA-Z])([0-9a-zA-Z][0-9a-zA-Z])([0-9a-zA-Z][0-9a-zA-Z])')


def as_color(col_str):
    """Get reportlab color from string.

    Supported formats are:
    1. Color name defined in reportlab.lib.colors.getAllNamedColors()
    2. tuple of RGB values in float, such as (1.0, 0.5, 0.25).
    3. #-prefixed hexdigits, such as #33cc66.

    # Blue and BLUE is errournous, results in red (1,0,0)
    >>> as_color('blue'), as_color('Blue'), as_color('BLUE')
    (Color(0,0,1), Color(1,0,0), Color(1,0,0))
    >>> as_color('(0.25,0.125,0.75)')
    Color(.25,.125,.75)
    >>> as_color('#3399ff')
    Color(.2,.6,1)
    >>> as_color(''), as_color('nonexistent') # invalid format falls to red: (1,0,0).
    (Color(1,0,0), Color(1,0,0))
    >>> as_color(None) # Non-string value should fail in TypeError
    Traceback (most recent call last):
    ...
    TypeError: expected string or buffer
    """
    global allcols
    if col_str in allcols.keys():
        return allcols[col_str]
    color_tuple = (1, 0, 0) # red
    match = regex_t.search(col_str, 0)
    if match:
        return colors.Color(float(match.group(1)),
                            float(match.group(2)),
                            float(match.group(3)))
    match = regex_h.search(col_str, 0)
    if match:
        return colors.Color(*(float(int(match.group(i+1),16))/255
                              for i in range(3)))
    return colors.red
get = as_color # for backward compatibility


unit_patterns = [
    (re.compile('^(-?[0-9\.]+)\s*in$'), inch),
    (re.compile('^(-?[0-9\.]+)\s*cm$'), cm),  
    (re.compile('^(-?[0-9\.]+)\s*mm$'), mm),
    (re.compile('^(-?[0-9\.]+)\s*$'), 1),]
def as_pt(size):
    """Convert string into float value, parsing unit suffix.

    >>> as_pt('1in'), as_pt('1.cm'), as_pt('.25mm'), as_pt('1')
    (72.0, 28.346456692913385, 0.70866141732283472, 1.0)
    >>> as_pt('.25'), as_pt('1.'), as_pt('1.25')
    (0.25, 1.0, 1.25)
    >>> as_pt('1ml') # invalid format yields False
    0
    """
    for regexp, unit in unit_patterns:
        match = regexp.search(size, 0)
        if match:
            return unit*float(match.group(1))
    return 0
unit_get = as_pt # for backward compatibility: will be removed soon.


def getAttrAsIntTuple(node, attr_name, default=None):
    """Get node attribute and convert into tuple of integers.

    >>> from xml.dom.minidom import parseString
    >>> document = parseString('<foo bar="1,2,5" />')
    >>> node = document.childNodes[0]
    >>> getAttrAsIntTuple(node, 'bar')
    [1, 2, 5]
    >>> getAttrAsIntTuple(node, 'baz') # return nothing.
    >>> getAttrAsIntTuple(node, 'baz', (3,4,5))
    (3, 4, 5)
    """
    if not node.hasAttribute(attr_name):
        return default
    res = [int(x) for x in node.getAttribute(attr_name).split(',')]
    return res
tuple_int_get = getAttrAsIntTuple # for backward compatibility.


type_map = dict(str=unicode, bool=as_bool, int=int, text=unicode)
def getAttrsAsDict(node, attrs, typed_attrs={}):
    """Returns dictionary of values for given attributes.

    >>> from xml.dom.minidom import parseString
    >>> document = parseString('<foo spam="1" egg="1" bacon="1" />')
    >>> node = document.childNodes[0]
    >>> getAttrsAsDict(node, ('spam', 'egg', 'ham'))
    {'egg': 1.0, 'ham': 0, 'spam': 1.0}
    >>> getAttrsAsDict(node, ('spam', 'egg', 'bacon'), dict(spam='bool', egg='int'))
    {'bacon': 1.0, 'egg': 1, 'spam': True}
    """
    res = dict((akey, as_pt(node.getAttribute(akey))) for akey in attrs)
    res.update((akey, type_map[atype](node.getAttribute(akey)))
               for akey, atype in typed_attrs.items()
               if node.hasAttribute(akey))
    return res
attr_get = getAttrsAsDict # for backward compatibility: will be removed soon.


def getText(node):
    """Get text data from a node.

    >>> from xml.dom.minidom import parseString
    >>> document = parseString('<foo>a text</foo>')
    >>> node = document.childNodes[0]
    >>> getText(node)
    u'a text'
    """
    rc = ''
    for subnode in node.childNodes:
        if subnode.nodeType == subnode.TEXT_NODE:
            rc = rc + subnode.data
    return rc
text_get = getText # for backward compatibility: will be removed soon.


if __name__=="__main__":
    from doctest import testmod
    testmod()
