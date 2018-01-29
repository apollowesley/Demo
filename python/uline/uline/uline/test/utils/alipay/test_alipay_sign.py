#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import ioloop
from tornado import testing

from uline.utils.alipay import new_merchantInletToAlipay, query_alipay_mapi
from uline import settings


class AlipaySignTest(testing.AsyncTestCase):
    @testing.gen_test(timeout=20)
    def test_sign(self):
        biz_content = {"bank_card_no": '6228480402564890018', 'business_license_no': "31339",
                       "cert_no": "411722197303195710",
                       "risk_type": "riskinfo_cert_no,riskinfo_bank_card_no,riskinfo_business_license_no"}
        result = yield query_alipay_mapi.query_ali_mapi('customerrisk_query', biz_content, 'risk',
                                                        requred_param_key='required_keys',
                                                        crypto_type='RSA', charset='GBK')
        print result


    @testing.gen_test(timeout=20)
    def test_customer_risk_send(self):
        biz_content = {
            'smid': '659004198009128344',
            'process_code': '01'
        }

        result = yield query_alipay_mapi.query_ali_mapi('customerrisk_send', biz_content, 'risk',
                                                        requred_param_key='required_keys',
                                                        crypto_type='RSA', http_method="POST", charset='GBK')
        print result
