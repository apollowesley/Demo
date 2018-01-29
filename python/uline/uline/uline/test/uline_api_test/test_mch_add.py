#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: test_mch_add.nepy
# datetime: 2017/5/22 14:23
# description: 测试uline_api添加商户接口

from tornado.testing import gen_test, AsyncTestCase
from tornado.ioloop import IOLoop
from tornado import gen
from uline.public.db import initdb
from uline.utils.wxpay.query_wx import get_content_type
import json
from uline.public.common import create_or_update_merchant
from requests_toolbelt.multipart.encoder import MultipartEncoder


class AddMchTestCase(AsyncTestCase):
    def setUp(self):
        self.io_loop = IOLoop.current()
        initdb()
        self.mch_infos = {
            'mch_name': 'test_add_mch',
            'mch_shortname': 'test_add_mch_short',
            'industry_no': '161215010100006',
            'area': u'宝安区',
            'cmbProvince': u'广东省',
            'cmbCity': u'深圳市',
            'cmbArea': u'保安区',
            'province': u'广东省',
            'city': u'深圳市',
            'district': u'南山区',
            'address': u'深大地铁',
            'contact': u'联系人',
            'mobile': u'13788909086',
            'service_phone': u'13788909086',
            'email': u'13788909086@qq.com',
            'balance_type': u'2',
            'balance_name': u'test',
            'balance_account': u'6214850294965740',
            'bank_no': u'989584006609',
            'bankName': u'test',
            'id_card_no': u'430524199009097152',
            'wx_use_parent': u'1',
            'license_num': u"sdfasdf",
            'license_start_date': u'2017-01-03',
            'license_end_date': None,
            'license_period': u'2',
            'license_scope': u"test",
            'dt_sub_id': None,
            'cs_id': None,
            'use_dine': u'1',
        }

        self.d0_infos = {
            'wx': u'5',
            'alipay': u'5',
        }

        imgfile = '/Users/apple/code/uline/uline/static/uploads/mch/idcard/100000070011/4d48e3ce27924f67ac833550ed9ba3ab.jpg'
        import os
        import copy
        self.opend_file = open(imgfile, 'rb')
        file_content = self.opend_file.read()
        file_name = os.path.basename(imgfile)
        self.files = [
            ('license_img', (file_name, file_content, get_content_type(imgfile))),
            ('id_card_img_f', (file_name, file_content, get_content_type(imgfile))),
            ('id_card_img_b', (file_name, file_content, get_content_type(imgfile))),

            ('annex_img5', (file_name, file_content, get_content_type(imgfile))),
        ]

        self.mch_front_img = ('mch_front_img', (file_name, file_content, get_content_type(imgfile)))
        # 商户内部环境照片
        self.mch_inner_img = ('mch_inner_img', (file_name, file_content, get_content_type(imgfile)))
        self.mch_desk_img = ('mch_desk_img', (file_name, file_content, get_content_type(imgfile)))
        self.wx_dine_imgs = [self.mch_front_img, self.mch_desk_img, self.mch_inner_img]

        self.wx_dine_annex_imgs = [('wx_dine_annex_img1', (file_name, file_content, get_content_type(imgfile))), ]
        self.common_paytypes = {
            'use_dine': None,
            'payment_type1': '9990',
            'payment_type2': '666',
            'payment_type3': '666',
            'payment_type4': None,
            'payment_type5': None,
            'payment_type7': None,
            'payment_type8': None,
            'payment_type9': None,
            'payment_type101': None,
            'payment_type102': None,
            'payment_type103': None,
            'payment_type104': None,
            'payment_type105': None,
            'payment_type107': None,
            'payment_type108': None,
            'payment_type109': None,
        }

    def tearDown(self):
        self.opend_file.close()

    # @gen_test
    def stest_add_mch_dine(self):
        self.files.extend(self.wx_dine_annex_imgs)
        self.files.extend(self.wx_dine_imgs)
        for each_file in self.files:
            self.mch_infos[each_file[0]] = each_file[1]
        response_body = self.request_create_mch()
        self.assertEqual(response_body.get('code', 406), 200)

    def stest_add_mch_dine_without_annex(self):
        # self.files.extend(self.wx_dine_annex_imgs)
        self.files.extend(self.wx_dine_imgs)
        for each_file in self.files:
            self.mch_infos[each_file[0]] = each_file[1]
        response_body = self.request_create_mch()
        self.assertEqual(response_body.get('content').get('dine_annex_img'), [u'围餐商户必须传入至少一张围餐补充材料图片'])
        self.assertEqual(response_body.get('code', 406), 400)

    @gen_test
    def request_create_mch(self):
        multipart_data = MultipartEncoder(fields=self.mch_infos)
        method = 'POST'
        path = '/v1/mchinlet'
        api_id = '10000000830'
        api_key = '92c1466a1f71369ecc88a72f1b25bcf0'
        response_body = yield create_or_update_merchant(method, path, api_id, api_key, multipart_data)
        raise gen.Return(response_body)

    def test_common_mch_add(self):
        self.mch_infos.update(self.common_paytypes)
        for each_file in self.files:
            self.mch_infos[each_file[0]] = each_file[1]
        response_body = self.request_create_mch()
        print response_body
        self.assertEqual(response_body.get('code', 406), 200)

    def test_multi_mch_add(self):
        for i in range(1, 3000):
            self.test_common_mch_add()
