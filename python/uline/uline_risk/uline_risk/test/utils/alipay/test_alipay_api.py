#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: test_alipay_api.py
# datetime: 17/8/3 上午9:42
# description: 测试支付宝接口
from tornado import ioloop
from tornado import testing
from uline_risk.utils.db import initdb
from uline_risk.utils.alipay import query_alipay


class AlipayApiTest(testing.AsyncTestCase):
    def setUp(self):
        self.io_loop = ioloop.IOLoop.current()
        initdb()
        self.mch_id = '100000188431'
        self.mch_inlet_info = dict()
        # with uline_session_scope() as session:
        #     self.mch_inlet_info = session.query(MchInletInfo).filter(
        #         MchInletInfo.mch_id == int(self.mch_id)).first().to_dict()
        #     self.mch_user = session.query(MchUser).filter(
        #         MchUser.mch_id == int(self.mch_id)).first().to_dict()

    def test_get_ali_mch_info(self):
        query_args = {
            'risk_type': 'riskinfo_cert_no',
            'cert_no': '53292319741027097X'
        }
        result = query_alipay.ali_api_block(query_args, 'customerrisk_query')
        print(result)
