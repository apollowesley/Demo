#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import expanduser
import re

from uline_api import settings

bash_rc = ''
if os.path.exists(expanduser("~/.bashrc")):
    with open(expanduser("~/.bashrc")) as f:
        bash_rc += f.read()

if os.path.exists(expanduser("~/.bash_profile")):
    with open(expanduser("~/.bash_profile")) as f:
        bash_rc += f.read()

match = re.search(r'ULINE_API_ENV=(.+)', bash_rc)
env = match.group(1) if match else None


if env == 'DEV':
    from uline_api.etc.dev import *
elif env == 'LOCAL':
    from uline_api.etc.local import *
elif env == 'INSIDE':
    from uline_api.etc.inside import *
elif env == 'PROD':
    from uline_api.etc.prod import *
elif env == 'SPD_PROD':
    from uline_api.etc.spd_prod import *
elif env == 'DEV3':
    from uline_api.etc.dev3 import *
else:
    raise Exception(u'必须在~/.bashrc或~/.bash_profile中设置ULINE_API_ENV环境变量')

DEV = False if env == 'PROD' else True


# 有效的支付方式
AVAILABLE_PAYMENTS = {
    '1': u'微信－扫码支付',
    '2': u'微信－刷卡支付',
    '3': u'微信－公众账号支付',
    '4': u'微信－APP支付',
    '5': u'微信－H5支付',
    '6': u'微信某某支付',
    '7': u'支付宝－扫码支付',
    '8': u'支付宝－刷卡支付',
    '9': u'支付宝－JS支付',
    '21': u'京东－扫码支付',
    '22': u'京东－刷卡支付',
    '23': u'京东－公众账号支付',
    '33': u'银联－JS支付',
}

# 有效的支付类型
PAY_TYPES = [1, 2, 3, 4, 5, 7, 8, 9, 21, 22, 23, 33]

if FEATURE_SWITCH.get('OPEN_D0'):

    AVAILABLE_PAYMENTS.update({
        '101': u'D0-微信－扫码支付',
        '102': u'D0-微信－刷卡支付',
        '103': u'D0-微信－公众账号支付',
        '104': u'D0-微信－APP支付',
        '105': u'D0-微信－h5支付',
        '107': u'D0-支付宝－扫码支付',
        '108': u'D0-支付宝－刷卡支付',
        '109': u'D0-支付宝－JS支付'
    })

    PAY_TYPES += [101, 102, 103, 104, 105, 107, 108, 109]

# 围餐
DINE_PAYMENTS = {
    '11': u'围餐-微信－扫码支付',
    '12': u'围餐-微信－刷卡支付',
    '13': u'围餐-微信－公众账号支付',
}
DINE_PAY_TYPES = [11, 12, 13]
if FEATURE_SWITCH.get('DINE_TOGETHER', False):
    AVAILABLE_PAYMENTS.update(DINE_PAYMENTS)
    PAY_TYPES.extend(DINE_PAY_TYPES)
