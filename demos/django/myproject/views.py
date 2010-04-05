# coding: utf-8

from django.http import HttpResponse
from template2pdf.dj import direct_to_pdf

from django.shortcuts import render_to_response

def myview(request, template_name='herring.rml'):
    params = {}
    items = [
        dict(plu='s001', name=u'OMSK-1',
             desc=u'オオムラサキ',
             unit_price=12000, quantity=2),
        dict(plu='s023', name=u'SRBY-25',
             desc=u'シャリンバイ',
             unit_price=3000, quantity=15),
        dict(plu='s057', name=u'JJGE-7',
             desc=u'ジンチョウゲ',
             unit_price=2500, quantity=8),
        dict(plu='s008', name=u'NTN-2',
             desc=u'ナンテン',
             unit_price=12000, quantity=12),
        ]

    for item in items:
        item['subtotal'] = item['unit_price']*item['quantity']

    params['items'] = items
    params['price'] = sum(item['subtotal'] for item in items)
    from reportlab.pdfbase.ttfonts import TTFont
    resolver = lambda t, x: TTFont(
        x.get('faceName'),
        '/Library/Fonts/Microsoft/'+x.get('fileName'),
        x.get('subfontIndex'))
    return HttpResponse(
        direct_to_pdf(request, template_name, params),
        mimetype='application/pdf')
