#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: test_query_wx.py
# datetime: 2017/5/22 14:23
# description: 测试微信相关问题


from tornado import ioloop
from tornado import testing

from uline.model.uline.info import MchInletInfo
from uline.model.uline.user import MchUser
from uline.public.db import initdb
from uline.public.db import uline_session_scope
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
)
from uline.utils.wxpay import query_wx
from uline.utils.wxpay.util import deal_with_wx_result
from uline.public import common


class WxQueryTestCase(testing.AsyncTestCase):
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

    def atest_get_lack_args(self):
        args = {

        }
        need_keys = ['s']
        result = query_wx.get_lack_args(args, need_keys)
        self.assertTrue(result)
        args = {'s': 's'}
        result = query_wx.get_lack_args(args, need_keys)
        self.assertFalse(result)

    @testing.gen_test
    def stest_get_mch_info(self):
        args = {
            'appid': APPID,
            'mch_id': WX_MCH_ID,
            'sub_mch_id': self.mch_user.get('wx_sub_mch_id'),
        }
        result = yield query_wx.get_wx_mch_info(args, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        self.assertTrue(result.get("total", 0))

    @testing.gen_test
    def stest_modify_wx_info(self):
        with uline_session_scope() as session:
            mch_id = '100000148722'
            result = session.query(MchInletInfo).filter(
                MchInletInfo.mch_id == int(mch_id)).first()
            short_name = result.mch_shortname
            service_phone = result.service_phone
            contact = 'test'
            args = {
                'appid': APPID,
                'mch_id': WX_MCH_ID,
                'sub_mch_id': self.mch_user.get('wx_sub_mch_id'),
                "merchant_shortname": short_name,
                "service_phone": service_phone,
                'contact': result.contact
            }
            result = yield query_wx.modify_wx_mch_info(args, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
            self.assertEqual(result.get('result_code', ''), 'SUCCESS')

    @testing.gen_test
    def test_create_wx_mch(self):
        args = {
            "merchant_name": self.mch_inlet_info.get('mch_name'),
            "merchant_shortname": self.mch_inlet_info.get('mch_shortname'),
            "service_phone": self.mch_inlet_info.get('service_phone'),
            'contact': self.mch_inlet_info.get('contact'),
            "contact_phone": self.mch_inlet_info.get('mobile'),
            "contact_email": self.mch_inlet_info.get('email'),
            "business": self.mch_inlet_info.get('wx_ind_code'),
            "merchant_remark": self.mch_id,
            'channel_id': '1231'
        }
        wx_result = query_wx.query_wx_api_block(args, query_type='create_mch', channel=2)
        self.assertIsNotNone(wx_result)

    @testing.gen_test
    def test_query_mch_config_common(self):
        wx_sub_id = self.mch_user.get('wx_sub_mch_id')
        query_args = {
            'sub_mch_id': wx_sub_id
        }
        result = query_wx.query_wx_api_block(query_args, query_type='querysubdevconfig')
        self.assertIsNotNone(result)
        result = deal_with_wx_result(result, 'jsapi_path_list', 'xx')
        self.assertIsNotNone(result[0])

    def get_content_type(self, filename):
        import mimetypes
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    @testing.gen_test
    def stest_upload_pictures_api(self):
        imgfile = '/Users/apple/code/uline/uline/static/uploads/mch/idcard/100000070011/4d48e3ce27924f67ac833550ed9ba3ab.jpg'
        import os
        import hashlib
        md5info = hashlib.md5()
        with open(imgfile, 'rb') as f:
            file_content = f.read()
            md5info.update(file_content)
            file_md5 = md5info.hexdigest()

            file_headers = dict()
            file_headers['filename'] = f.name
            file_headers['filelength'] = len(file_content)
            files = [('media', (os.path.basename(imgfile), file_content, query_wx.get_content_type(imgfile), file_headers))]

            args = {
                "media_hash": file_md5,
            }
            result = query_wx.query_wx_use_form(args, 'uploadpicturesapi', ['mch_id'], files)
            self.assertIsNotNone(result)

    @testing.gen_test
    def stest_green_plan_get_new_cs(self):
        query_args = {
            'sub_mch_id': '36979256',
            'shop_name': 'test',
            'shop_address_code': '110115',
            'shop_street': 'ssssss',
            'nonce_str': common.gen_random_str(),
            'shop_entrance_pic': "MZPUO0HONxwyvQafQt5EOK9ekt0x-V3HJfJMC-FeSc-vySuJD630AhQr_YU_nYDxnQ38PMaYU9dqRQS775YRdZ_S2iFsSuCpznqwBv0qcrI",
            'checkstand_pic': "MZPUO0HONxwyvQafQt5EOK9ekt0x-V3HJfJMC-FeSc-vySuJD630AhQr_YU_nYDxnQ38PMaYU9dqRQS775YRdZ_S2iFsSuCpznqwBv0qcrI",
            'business_license_pic': "MZPUO0HONxwyvQafQt5EOK9ekt0x-V3HJfJMC-FeSc-vySuJD630AhQr_YU_nYDxnQ38PMaYU9dqRQS775YRdZ_S2iFsSuCpznqwBv0qcrI",
            'indoor_pic': "MZPUO0HONxwyvQafQt5EOK9ekt0x-V3HJfJMC-FeSc-vySuJD630AhQr_YU_nYDxnQ38PMaYU9dqRQS775YRdZ_S2iFsSuCpznqwBv0qcrI",
        }
        print query_args['nonce_str'], len(query_args['nonce_str'])
        import pdb
        pdb.set_trace()
        result = query_wx.query_wx_api_block(query_args, 'greenplangetnewcs', channel=10)

    @testing.gen_test
    def stest_modify_cs_profile(self):
        args = {
            'sub_mch_id': "",
            'mch_id': WX_MCH_ID,
            'shop_name': "",
            'shop_id': "",
            'shop_address_code': "",
            'shop_street': "",
            'shop_entrance_pic': "",
            'checkstand_pic': "",
            'business_license_pic': "",
            'indoor_pic': "",
            'nonce_str': "",
            'sign': ""
        }
        wx_result = yield query_wx.modify_cs_profile(args, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)

    @testing.gen_test
    def stest_query_auth_result(self):
        query_args = {
            'sub_mch_id': "36979256",
            'shop_id': "1200106692",
            'nonce_str': common.gen_random_str(),
        }
        wx_result = query_wx.query_wx_api_block(query_args, 'queryauthresult', channel=10)
        print wx_result
