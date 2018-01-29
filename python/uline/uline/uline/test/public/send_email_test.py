#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.testing import gen_test, AsyncTestCase

from uline.public import active_email
from tornado.ioloop import IOLoop


class SendEmailTestCase(AsyncTestCase):
    def setUp(self):
        self.io_loop = IOLoop.current()
        self.mch_info = {
            'email': u'leiyutian@ulaiber.com',
            'mch_name': u'雷雨田的商户',
            'mch_id': 2312312,
            'mch_pay_key': 'sdf'
        }
        self.env = 'SPD_PROD'

    @gen_test
    def test_send_email(self):
        data = {
            'env': self.env,
            'reciver': self.mch_info['email'],
            'title': u'uline商户激活信息',
            'body': 'test'
        }
        response = yield active_email.send_email(data)
        self.assertEqual('2', response.body)

    @gen_test
    def test_send_mch_active_email(self):
        response = yield active_email.send_active_mch_email(self.env, self.mch_info)
        self.assertEqual('2', response.body)
