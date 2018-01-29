#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from uline import settings
from uline.model.uline.info import PlatformMch
from uline.public.db import initdb
from uline.public.db import uline_session_scope


def init_config(session):
    # 微信:
    # 千二通道
    WX_OFFLINE_KEYS = {"mch_id": 'WX_MCH_ID', 'app_id': 'APPID', 'pay_key': 'WXPAY_KEY', 'pub_key': 'WX_PUB_KEY',
                       'private_key': 'WX_PRIVATE_KEY', 'pay_channel': 'weixin', 'channel_code': 2, 'settle_rate': 20}

    # 千6通道
    WX_ONLINE_KEYS = {"mch_id": 'WX_APP_MCH_ID', 'app_id': 'WX_APP_APPID', 'pay_key': 'WXPAY_APP_KEY',
                      'pub_key': 'WX_APP_PUB_KEY', 'private_key': 'WX_APP_PRIVATE_KEY', 'pay_channel': 'weixin',
                      'channel_code': 6, 'settle_rate': 60}

    # 0费率通道
    WX_ZERO_KEYS = {"mch_id": 'WX_0_WX_MCH_ID', 'app_id': 'WX_0_APPID', 'pay_key': 'WX_0_WXPAY_KEY',
                    'pub_key': 'WX_0_PUB_KEY', 'private_key': 'WX_0_PRIVATE_KEY',
                    'pay_channel': 'weixin', 'channel_code': 0, 'settle_rate': 0}

    # 微信围餐通道
    WX_DINE_KEYS = {'mch_id': 'WX_DINE_WX_MCH_ID', 'app_id': 'WX_DINE_APPID', 'pay_key': 'WX_DINE_WXPAY_KEY',
                    'pub_key': 'WX_DINE_PUB_KEY', 'private_key': 'WX_DINE_PRIVATE_KEY',
                    'pay_channel': 'weixin', 'channel_code': 10, 'settle_rate': 0}

    # 支付宝通道
    ALIPAY_OFFLINE_KEYS = {'mch_id': 'ALI_PID', 'app_id': 'ALI_APPID', 'pub_key': 'ALI_PUB_KEY',
                           'private_key': 'ALI_PRIVATE_KEY',
                           'pay_channel': 'alipay', 'channel_code': 2, 'settle_rate': 20}

    setting_keys = ['mch_id', 'app_id', 'pay_key', 'pub_key', 'private_key']
    for each_config in [WX_OFFLINE_KEYS, WX_ONLINE_KEYS, WX_ZERO_KEYS, WX_DINE_KEYS, ALIPAY_OFFLINE_KEYS]:
        config_info = dict()
        for each_key in each_config:
            config_value = each_config.get(each_key, None)
            if each_key in setting_keys:
                setting_value = getattr(settings, config_value, None)
                if os.path.isfile(setting_value):
                    key_file = open(setting_value, 'r')
                    config_info[each_key] = key_file.read()
                    key_file.close()
                else:
                    config_info[each_key] = setting_value
            else:
                config_info[each_key] = config_value

        session.add(PlatformMch(**config_info))


if __name__ == "__main__":
    initdb()
    with uline_session_scope() as session:
        # 删除所有配置先
        session.query(PlatformMch).delete()
        init_config(session)
