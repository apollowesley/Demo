#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: wx_config_util.py
# datetime: 2017/7/3 08:41
# description: 微信配置
import json

from uline.utils.wxpay import wx_util
from uline.public import log
from uline.utils.json_utils import LazableJSONEncoder

from tornado import gen


CONFIGS = ['jsapi_path', 'subscribe_appid', 'sub_appid']

CHANNEL_MAP = {
    2: '线下通道',
    6: '线上通道',
    10: '围餐',
}


def save_config(cursor, config_info):
    sql = """INSERT INTO pay_config_info(role_id, role_type, config_name, config_value, channel, create_time, update_time)
             VALUES
             (%(role_id)s, %(role_type)s, %(config_name)s, %(config_value)s, %(channel)s, %(create_time)s, %(update_time)s);"""
    cursor.execute(sql, config_info)


def get_wx_configs(cursor, role_id, role_type, channel):
    sql = """SELECT config_name, config_value FROM pay_config_info WHERE role_id=%s AND role_type=%s AND channel=%s;"""
    cursor.execute(sql, (role_id, role_type, channel))
    result = cursor.fetchall()
    wx_configs = {}
    jsapi_path_list = []
    appid_config_list = []
    default_subscribe = ''
    for each_config in result:
        config_name = each_config['config_name']
        config_value = each_config['config_value']
        if config_name == 'jsapi_path':
            jsapi_path_list.append(config_value)
        elif config_name == 'sub_appid':
            appid_config_list.append({'sub_appid': config_value})
        elif config_name == 'subscribe_appid':
            default_subscribe = config_value

    wx_configs['jsapi_path_list'] = jsapi_path_list or []
    # [{'sub_appid':'23123132123123123'},{'sub_appid':'123123123123'}]
    wx_configs['appid_config_list'] = appid_config_list or []
    wx_configs['default_subscribe'] = default_subscribe or ''
    wx_configs['wx_msg'] = ''
    wx_configs['channel_type'] = channel
    wx_configs['channel_name'] = CHANNEL_MAP[channel]
    return wx_configs


@gen.coroutine
def refresh_wx_config(cursor, role_id, role_type, sub_mch_id, channel, create_time):
    sql = """DELETE FROM pay_config_info WHERE role_id=%s AND role_type=%s AND channel=%s;"""
    cursor.execute(sql, (role_id, role_type, channel))
    wx_configs = yield wx_util.get_wx_configs(sub_mch_id, channel)
    if wx_configs['wx_msg']:
        log.exception.err('get wx config err:{}'.format(wx_configs['wx_msg']))
        raise gen.Return(wx_configs['wx_msg'])
    else:
        js_api_paths = wx_configs.get('jsapi_path_list', [])
        appid_list = wx_configs.get('appid_config_list', [])
        default_subscribe = wx_configs['default_subscribe']
        config_value_list = list()
        for each_js_api in js_api_paths:
            config_info = {
                'role_id': role_id,
                'role_type': role_type,
                'config_name': 'jsapi_path',
                'config_value': each_js_api,
                'channel': channel,
                'create_time': create_time,
                'update_time': create_time
            }
            config_value_list.append(config_info)
        for each_appid in appid_list:
            sub_id = each_appid.get('sub_appid', '')
            if sub_id:
                config_info = {
                    'role_id': role_id,
                    'role_type': role_type,
                    'config_name': 'sub_appid',
                    'config_value': sub_id,
                    'channel': channel,
                    'create_time': create_time,
                    'update_time': create_time
                }
                config_value_list.append(config_info)
        if default_subscribe:
            default_subscribe_info = {
                'role_id': role_id,
                'role_type': role_type,
                'config_name': 'subscribe_appid',
                'config_value': default_subscribe,
                'channel': channel,
                'create_time': create_time,
                'update_time': create_time
            }
            config_value_list.append(default_subscribe_info)
        for each_config_info in config_value_list:
            save_config(cursor, each_config_info)
        raise gen.Return('')
