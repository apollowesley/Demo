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
from uline.public.db import initdb
from uline.utils.alipay import query_alipay
from uline.public.db import uline_session_scope
from uline.model.uline.info import MchInletInfo
from uline.model.uline.user import MchUser


class AlipayApiTest(testing.AsyncTestCase):
    def setUp(self):
        self.io_loop = ioloop.IOLoop.current()
        initdb()
        self.mch_id = '100000188431'
        self.mch_inlet_info = dict()
        with uline_session_scope() as session:
            self.mch_inlet_info = session.query(MchInletInfo).filter(
                MchInletInfo.mch_id == int(self.mch_id)).first().to_dict()
            self.mch_user = session.query(MchUser).filter(
                MchUser.mch_id == int(self.mch_id)).first().to_dict()

    def dtest_get_ali_mch_info(self):
        query_args = {
            'risk_type': 'riskinfo_cert_no',
            'cert_no': '53292319741027097X'
        }
        result = query_alipay.ali_api_block(query_args, 'customerrisk_query')
        print result

    def test_update_mch_info(self):
        query_dict = {'external_id': self.mch_id, 'name': self.mch_inlet_info['mch_name'],
                      'alias_name': self.mch_inlet_info['mch_shortname'],
                      'service_phone': self.mch_inlet_info['service_phone'] or self.mch_inlet_info['mobile'],
                      'source': '2088102169373866',
                      'category_id': self.mch_inlet_info['ali_ind_code']}

        # 如果有填区域信息，则以M2等级进件
        result = query_alipay.ali_api_block(query_dict, 'indirect_modify', level="M1")
        print result
