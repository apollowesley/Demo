#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 该示例仅用于演示如何进行认证授权

import random
import requests
from datetime import datetime
from hashlib import md5
from requests_toolbelt.multipart.encoder import MultipartEncoder


API_URL = 'http://127.0.0.1:9901/v1/mchinlet'
API_ID = '10000000830'
API_KEY = '7290C9989626D3D78496CA831FDAB3CC'

multipart_data = MultipartEncoder(
    fields={
        'mch_name': u'测试用户名',
        'mch_shortname': u'测试简称',
        'industry_no': '123',
        'province': u'广东省',
        'city': u'深圳市',
        'address': u'我是地址',
        'contact': u'联系人',
        'mobile': ''.join(str(random.randint(1, 9)) for _ in range(13)),
        'service_phone': ''.join(str(random.randint(1, 9)) for _ in range(13)),
        'email': 'email@gmail.com',
        'balance_type': '1',
        'balance_name': u'名称',
        'bank_no': '124532634436',
        'balance_account': '124532634436',
        'id_card_no': '154375487698770',
        'id_card_img_f': ('id_card_img_f.jpg', 'demo', 'text/plain'),
        'id_card_img_b': ('id_card_img_b.jpg', 'demo', 'text/plain'),
        'license_img': ('license_img.jpg', 'demo', 'text/plain'),
        'wx_use_parent': '1',
        'payment_type1': '60',
        'payment_type2': '60',
        'payment_type3': '60',
        'license_num': '125346457659760',
        'license_start_date': '2016-11-11',
        'license_period': '1',
        'license_scope': u'测试经营范围'
    }
)
date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

method = 'POST'
path = '/v1/mchinlet'

sign_body = '&'.join([method, path, date, str(multipart_data.len), API_KEY])
sign = md5(sign_body).hexdigest()

headers = {
    'Authorization': 'Uline ' + API_ID + ':' + sign,
    'Date': date,
    'Content-Type': multipart_data.content_type,
}

ret = requests.post(API_URL, data=multipart_data, headers=headers)
print(ret.json())
