#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy

import qrcode
from cStringIO import StringIO
from contextlib import closing
from tornado.web import authenticated
from uline.handlers.baseHandlers import CommanHandler


def generate_qrcode(text, size):
    with closing(StringIO()) as sio:
        qr_img = qrcode.make(text, **{'version': 1,
                                      'error_correction': qrcode.constants.ERROR_CORRECT_L,
                                      'box_size': int(size),
                                      'border': 0, }).resize((int(size), int(size)))
        qr_img.save(sio, format='JPEG')
        return sio.getvalue()


class QrDownload(CommanHandler):

    @authenticated
    def get(self):
        qr_text = self.get_argument('text', 'http://www.uline.cc')
        name = self.get_argument('save_name', 'uline_cc.jpg')
        size = self.get_argument('size', 200)
        body = generate_qrcode(qr_text, size)
        self.set_header('content_type', 'application/octet-stream')
        self.set_header('Content-Disposition',
                        'attachment; filename={}'.format(name))
        self.write(body)
