# coding: utf-8

import os
import sys
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), 'trunk'))

from template2pdf.fsk import direct_to_pdf
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def demo():
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
    return direct_to_pdf('base.rml', params)


if __name__=='__main__':
    app.run(debug=True)
