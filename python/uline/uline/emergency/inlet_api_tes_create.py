# -*- coding: utf-8 -*-
import requests
import datetime
from hashlib import md5
from requests_toolbelt.multipart.encoder import MultipartEncoder

m = MultipartEncoder(fields={'mch_name': '测试进件1009', 'mch_shortname': '随便叫吧', 'city': '深圳', 'province': '广东省',
                             'address': '123', 'mobile': '15920170139', 'email': '916351452@qq.com', 'service_phone': '010-6312122', 'bank_no': '001100001509',
                             'industry_no': '161215010100001', 'balance_type': '1', 'balance_name': '909', 'balance_account': '6228480128086840971',
                             'id_card_no': '110', 'contact': '郭志华', 'notify_url': 'http://abc.com',
                             'father_name': 'dt',
                             # old
                             'payment_type101': '26', 'payment_type102': '26', 'payment_type103': '26',
                             # 'payment_type107': '700',
                             # 'alipay': '200',
                             'wx': '21',
                             # 'payment_type108': '800', 'payment_type109': '900',
                             # 'wx': '100', 'alipay': '200',
                             # new
                             # 'WX_OFFLINE_NATIVE': '200', 'WX_OFFLINE_MICROPAY': '300', 'WX_OFFLINE_JSAPI': '400',
                             # 'WX_ONLINE_APP': '500',
                             # #'WX_ONLINE_MWEB':'600',
                             # 'ALI_OFFLINE_NATIVE': '700', 'ALI_OFFLINE_MICROPAY': '800', 'ALI_OFFLINE_JSAPI': '900',
                             # 'wx_draw_fee': '100', 'ali_draw_fee': '200',
                             # 'wx_draw_rate': '200', 'ali_draw_rate': '300',
                             'license_num': '110', 'license_start_date': '2017-8-30',\
                             'license_period': '1', 'license_scope': '111', 'id_card_img_f': ('file', open('/Users/apple/Downloads/1.jpg', 'rb'), 'multipart/form-data'),\
                             'id_card_img_b': ('file', open('/Users/apple/Downloads/1.jpg', 'rb'), 'multipart/form-data'),\
                             'license_img': ('file', open('/Users/apple/Downloads/1.jpg', 'rb'), 'multipart/form-data')},\
                     boundary='---------------------------7de1ae242c06ca')


def gettime():
    GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
    # 生成datetime对象的过程和我可能不同，这里是拿当前时间来生成
    t = datetime.datetime.utcnow().strftime(GMT_FORMAT)
    return t


def getkey():
    # 本地
    str1 = 'POST&/v1/mchinlet&' + gettime() + '&' + str(m.len) + '&72b5b6c65ecd7ffd41128d8738b019a6'
    # 测试
    # str1 = 'POST&/v1/mchinlet&' + gettime() + '&' + str(m.len) + '&164021c54ba4ddb2e54d6e3c843d0a05'
    sss = md5(str1.encode('utf8')).hexdigest()
    return sss

# 安全认证
# 本地
URL = 'http://127.0.0.1:9901/v1/mchinlet'
API_ID = '10000080315'
# 测试
# URL = 'http://pay.stage.uline.cc/v1/mchinlet'
# API_ID = '10000294200'
val = 'Uline ' + API_ID + ':' + getkey()
HEADERS = {'Authorization': val, 'Date': gettime(), 'Content-Type': m.content_type}

r = requests.post(url=URL, headers=HEADERS, data=m)
print(r.json())
