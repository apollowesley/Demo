#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: constants.py
# datetime: 17/8/3 下午8:06
# description: 常量

AUTH_STATUS = {'1': '初审中', '2': '审核通过', '3': '复审驳回', '4': '复审中', '5': '进件中', '6': '进件失败', '7':'初审驳回'}
AUTH_STATUS_SUBMIT = 1
AUTH_STATUS_ACCEPT = 2
AUTH_STATUS_DENY = 3
AUTH_STATUS_REVIEWING = 4
AUTH_STATUS_INLETING = 5
AUTH_STATUS_INTERNET_FAIL = 6
AUTH_STATUS_FIRST_DENY = 7


translate_payment_type = {
    # payment_type : 'uline_payment_id|uline_settle_id|trade_type|platform_mch_id|uline_payment_code'

    # d1 微信
    1: '1|1|NATIVE|1|WX_OFFLINE_NATIVE',
    2: '2|1|MICROPAY|1|WX_OFFLINE_MICROPAY',
    3: '3|1|JSAPI|1|WX_OFFLINE_JSAPI',

    4: '4|1|APP|2|WX_ONLINE_APP',
    5: '5|1|MWEB|2|WX_ONLINE_MWEB',

    # d1 支付宝
    7: '7|1|NATIVE|5|ALI_OFFLINE_NATIVE',
    8: '8|1|MICROPAY|5|ALI_OFFLINE_MICROPAY',
    9: '9|1|JSAPI|5|ALI_OFFLINE_JSAPI',

    # d1 围餐
    11: '11|1|NATIVE|4|WX_DINE_NATIVE',
    12: '12|1|MICROPAY|4|WX_DINE_MICROPAY',
    13: '13|1|JSAPI|4|WX_DINE_JSAPI',

    # d1 围餐
    14: '14|1|NATIVE|3|WX_ZERO_NATIVE',
    15: '15|1|MICROPAY|3|WX_ZERO_MICROPAY',
    16: '16|1|JSAPI|3|WX_ZERO_JSAPI',

    17: '17|1|NATIVE|2|WX_ONLINE_NATIVE',
    18: '18|1|JSAPI|2|WX_ONLINE_JSAPI',

    # d1 微信
    21: '21|1|NATIVE|7|JD_OFFLINE_NATIVE',
    22: '22|1|MICROPAY|7|JD_OFFLINE_MICROPAY',
    23: '23|1|JSAPI|7|JD_OFFLINE_JSAPI',

    24: '24|1|H5|7|JD_ONLINE_H5',
    25: '25|1|H5_DEBIT|7|JD_ONLINE_H5_DEBIT',

    # 支付宝零费率
    27: '27|1|NATIVE|6|ALI_ZERO_NATIVE',
    28: '28|1|MICROPAY|6|ALI_ZERO_MICROPAY',
    29: '29|1|JSAPI|6|ALI_ZERO_JSAPI',

    33: '33|1|JSAPI|9|UNIONPAY_OFFLINE_JSAPI',

    # d0 微信
    101: '1|2|NATIVE|1|WX_OFFLINE_NATIVE',
    102: '2|2|MICROPAY|1|WX_OFFLINE_MICROPAY',
    103: '3|2|JSAPI|1|WX_OFFLINE_JSAPI',
    104: '4|2|APP|2|WX_ONLINE_APP',
    105: '5|2|MWEB|2|WX_ONLINE_MWEB',

    # d0 支付宝
    107: '7|2|NATIVE|5|ALI_OFFLINE_NATIVE',
    108: '8|2|MICROPAY|5|ALI_OFFLINE_MICROPAY',
    109: '9|2|JSAPI|5|ALI_OFFLINE_JSAPI',

    # d1 围餐
    111: '111|2|MICROPAY|4|WX_DINE_NATIVE',
    112: '112|2|MICROPAY|4|WX_DINE_MICROPAY',
    113: '113|2|MICROPAY|4|WX_DINE_JSAPI',

    117: '17|2|NATIVE|2|WX_ONLINE_NATIVE',
    118: '18|2|JSAPI|2|WX_ONLINE_JSAPI',

}

NEW_AVAILABLE_PAYMENTS = {
    # 微信线下支付
    'WX_OFFLINE_NATIVE': u'微信-扫码支付(线下D1)',
    'WX_OFFLINE_MICROPAY': u'微信-刷卡支付(线下D1)',
    'WX_OFFLINE_JSAPI': u'微信-公众账号支付(线下D1)',

    # 微信线上支付
    'WX_ONLINE_NATIVE': u'微信-扫码支付(线上D1)',
    'WX_ONLINE_JSAPI': u'微信-公众账号支付(线上D1)',
    'WX_ONLINE_APP': u'微信-APP支付(线上D1)',
    'WX_ONLINE_MWEB': u'微信-H5支付(线上D1)',

    # 微信围餐
    'WX_DINE_NATIVE': u'微信-扫码支付(围餐)',
    'WX_DINE_MICROPAY': u'微信-刷卡支付(围餐)',
    'WX_DINE_JSAPI': u'微信-公众账号支付(围餐)',

    # 微信零费率
    'WX_ZERO_NATIVE': u'微信-扫码支付(零费率)',
    'WX_ZERO_MICROPAY': u'微信-刷卡支付(零费率)',
    'WX_ZERO_JSAPI': u'微信-公众账号支付(零费率)',

    # 支付宝线下
    'ALI_OFFLINE_NATIVE': u'支付宝-扫码支付(线下D1)',
    'ALI_OFFLINE_MICROPAY': u'支付宝-刷卡支付(线下D1)',
    'ALI_OFFLINE_JSAPI': u'支付宝-JS支付(线下D1)',

    # 支付宝线下
    'JD_OFFLINE_NATIVE': u'京东-扫码支付(线下T1)',
    'JD_OFFLINE_MICROPAY': u'京东-刷卡支付(线下T1)',
    'JD_OFFLINE_JSAPI': u'京东-公众账号支付(线下T1)',

    # 京东线上
    'JD_ONLINE_H5': u'京东-H5支付（线下T1）',
    'JD_ONLINE_H5_DEBIT': u'京东-H5支付（借记卡)(线下T1）',

    # d0 (临时，后期将删除)
    # 微信线下支付
    'WX_OFFLINE_NATIVE_D0': u'微信-扫码支付(线下D0)',
    'WX_OFFLINE_MICROPAY_D0': u'微信-刷卡支付(线下D0)',
    'WX_OFFLINE_JSAPI_D0': u'微信-公众账号支付(线下D0)',

    # 微信线上支付
    'WX_ONLINE_NATIVE_D0': u'微信-扫码支付(线上D0)',
    'WX_ONLINE_JSAPI_D0': u'微信-公众账号支付(线上D0)',
    'WX_ONLINE_APP_D0': u'微信-APP支付(线上D0)',
    'WX_ONLINE_MWEB_D0': u'微信-H5支付(线上D0)',

    # 支付宝线下
    'ALI_OFFLINE_NATIVE_D0': u'支付宝-扫码支付(线下D0)',
    'ALI_OFFLINE_MICROPAY_D0': u'支付宝-刷卡支付(线下D0)',
    'ALI_OFFLINE_JSAPI_D0': u'支付宝-JS支付(线下D0)',

    'UNIONPAY_OFFLINE_JSAPI': u'银联-JS支付(线下D1)',
}


old_payment_relations = {
    # d1
    # 微信线下
    '1': 'WX_OFFLINE_NATIVE',
    '2': 'WX_OFFLINE_MICROPAY',
    '3': 'WX_OFFLINE_JSAPI',


    # 微信线上支付
    '17': 'WX_ONLINE_NATIVE',
    '18': 'WX_ONLINE_JSAPI',
    '4': 'WX_ONLINE_APP',
    '5': 'WX_ONLINE_MWEB',

    # 支付宝线下
    '7': 'ALI_OFFLINE_NATIVE',
    '8': 'ALI_OFFLINE_MICROPAY',
    '9': 'ALI_OFFLINE_JSAPI',

    # 微信围餐
    '11': 'WX_DINE_NATIVE',
    '12': 'WX_DINE_MICROPAY',
    '13': 'WX_DINE_JSAPI',

    # 微信0费率
    '14': 'WX_ZERO_NATIVE',
    '15': 'WX_ZERO_MICROPAY',
    '16': 'WX_ZERO_JSAPI',

    # 京东线上
    '21': 'JD_OFFLINE_NATIVE',
    '22': 'JD_OFFLINE_MICROPAY',
    '23': 'JD_OFFLINE_JSAPI',

    # 京东线上
    '24': 'JD_ONLINE_H5',
    '25': 'JD_ONLINE_H5_DEBIT',

    # 支付宝零费率
    '27': 'ALI_ZERO_NATIVE',
    '28': 'ALI_ZERO_MICROPAY',
    '29': 'ALI_ZERO_JSAPI',

    # 银联支付
    '33': 'UNIONPAY_OFFLINE_JSAPI',

    # d0
    # 微信线下
    '101': 'WX_OFFLINE_NATIVE_D0',
    '102': 'WX_OFFLINE_MICROPAY_D0',
    '103': 'WX_OFFLINE_JSAPI_D0',


    # 微信线上支付
    '117': 'WX_ONLINE_NATIVE_D0',
    '118': 'WX_ONLINE_JSAPI_D0',
    '104': 'WX_ONLINE_APP_D0',
    '105': 'WX_ONLINE_MWEB_D0',

    # 支付宝线下
    '107': 'ALI_OFFLINE_NATIVE_D0',
    '108': 'ALI_OFFLINE_MICROPAY_D0',
    '109': 'ALI_OFFLINE_JSAPI_D0',

    # 微信围餐
    '111': 'WX_DINE_NATIVE_D0',
    '112': 'WX_DINE_MICROPAY_D0',
    '113': 'WX_DINE_JSAPI_D0',

    # # 微信0费率
    # '114': 'WX_ZERO_NATIVE_D0',
    # '115': 'WX_ZERO_MICROPAY_D0',
    # '116': 'WX_ZERO_JSAPI_D0',
}

new_payment_relations = dict([(v, int(k)) for k, v in old_payment_relations.iteritems()])