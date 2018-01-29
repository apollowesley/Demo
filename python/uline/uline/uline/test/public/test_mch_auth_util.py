#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from tornado.testing import gen_test, AsyncTestCase
from tornado.ioloop import IOLoop

from uline.public import active_email, auth_util
from uline.model.uline.base import uline_session
from uline.public.db import initdb
from uline.model.uline import info
from mock import patch
from uline.model.uline.other import ChangeRecord


class SendEmailTestCase(AsyncTestCase):
    def setUp(self):
        initdb()
        self.io_loop = IOLoop.current()
        self.mch_id = 100000662987
        self.mch_auth_util = auth_util.MchAuthUtil(uline_session, 10000001, 100000662987)
        self.need_save = True

    def test_mch_auth(self):
        # self.mch_auth_util.change_record['mch_name'] = 'test_util'
        # self.mch_auth_util.change_record['email'] = 'test_util'
        # self.mch_auth_util.change_record['balance_info'] = {'balance_account': 'sdfasdasdf'}
        # self.mch_auth_util.change_record['role'] = {'wx': 11}
        import random
        rate = random.randint(1, 1000)
        data =  {
            "1": {"pay_type": 1, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "2": {"pay_type": 2, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "3": {"pay_type": 3, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "4": {"pay_type": 4, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "5": {"pay_type": 5, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "7": {"pay_type": 7, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "8": {"pay_type": 8, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "9": {"pay_type": 9, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},

            "101": {"pay_type": 101, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "102": {"pay_type": 102, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "103": {"pay_type": 103, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "104": {"pay_type": 104, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "105": {"pay_type": 105, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 2},
            "107": {"pay_type": 107, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "108": {"pay_type": 108, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
            "109": {"pay_type": 109, "pay_rate": rate, "activated_status": 1, "pre_status": 1, "action_type": 3},
        }

        change_data = json.dumps({'payment': data})
        change_record = ChangeRecord()
        change_record.mch_id = self.mch_auth_util.mch_id
        change_record.status = 1
        change_record.data_json = change_data
        change_record.change_type = 2
        uline_session.add(change_record)
        uline_session.commit()
        result = self.mch_auth_util.auth_mch()
        self.assertEqual(200, result.get('code', 406))

        # def test_update_withdraw_info(self):
        #     self.mch_auth_util.update_withdraw_info({'action_type': 1, 'wx': 13, 'alipay': 2})
        #
        # def test_update_extensions(self):
        #     self.mch_auth_util.change_record.update({'mch_front_img': 'sdfafd.ji'})
        #     self.mch_auth_util.update_extensions()
        #
        # def test_update_activated_status(self):
        #     self.mch_auth_util.update_activated_status()

        # def test_update_mch_payments(self):
        # record = {}
        # record['pay_type'] = 12
        # record['pay_rate'] = 0
        # record['pre_status'] = 2
        # record['action_type'] = 1
        # self.mch_auth_util.update_mch_payments({'12': record})
        #
        # record = {}
        # record['pay_type'] = 12
        # record['pay_rate'] = 1
        # record['pre_status'] = 2
        # record['action_type'] = 1
        # self.mch_auth_util.update_mch_payments({'12': record})
        # payments = uline_session.query(info.MchPayment).filter(info.MchPayment.mch_id == self.mch_id).all()
        # for each_payment in payments:
        #     print each_payment.payment_type,each_payment.payment_rate

        # record = {}
        # record['pay_type'] = 12
        # record['pay_rate'] = 1
        # record['pre_status'] = 2
        # record['action_type'] = 3
        # self.mch_auth_util.update_mch_payments({'12': record})

    def stest_query_dine_result(self):
        auth_status = self.mch_auth_util.query_wx_dine_result()
        print auth_status

    def tearDown(self):
        if self.need_save:
            uline_session.commit()
        uline_session.remove()
        self.io_loop.stop()
