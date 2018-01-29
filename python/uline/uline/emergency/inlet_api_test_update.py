#!/usr/bin/env python
# -*- coding:utf8 -*-

import requests
import datetime
from hashlib import md5
from requests_toolbelt.multipart.encoder import MultipartEncoder


m = MultipartEncoder(fields={'contact': '廖波诗', 'payment_type101': '999', 'license_period': '1', 'wx': '999',
                             'father_name': 'dt'},
                     boundary='---------------------------7de1ae242c06ca')


def gettime():
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    # 生成datetime对象的过程和我可能不同，这里是拿当前时间来生成
    t = datetime.datetime.utcnow().strftime(GMT_FORMAT)
    return t


def getkey():
    str1 = 'POST&/v1/mchinlet/update&' + gettime() + '&' + str(m.len) + '&72b5b6c65ecd7ffd41128d8738b019a6'
    sss = md5(str1.encode('utf8')).hexdigest()
    return sss

# 安全认证
URL = 'http://127.0.0.1:9901/v1/mchinlet/update'
API_ID = '10000080315'
val = 'Uline ' + API_ID + ':' + getkey()
HEADERS = {'Authorization': val, 'Date': gettime(), 'Content-Type': m.content_type}


payload = {'mch_id': 100035007962}

r = requests.post(url=URL, headers=HEADERS, data=m, params=payload)
print(r.json())
