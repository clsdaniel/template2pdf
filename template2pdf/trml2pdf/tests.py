# trml2pdf.test - An RML to PDF converter
# 
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

if __name__=="__main__":
    from doctest import testmod
    import trml2pdf
    testmod(trml2pdf)
    from os.path import abspath, dirname, join
    from os import chdir
    from glob import glob
    from warnings import warn
    chdir(join(dirname(dirname(abspath(__file__))), 'rmls'))
    for rml_fn in glob('*.rml'):
        try:
            # snap = file(rml_fn.replace('.rml', '.pdf'), 'rb').read()
            generated = trml2pdf.parseString(file(rml_fn, 'rb').read())
        except Exception, e:
            warn('Parsing %s failed due to: %s' %(rml_fn, str(e)))
