#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: wx_util.py
# datetime: 2017/6/19 14:40
# description: 查询微信后的处理

import json

import re
from tornado import gen

from uline_api.util.wxpay import query_wx
from uline_api.util.wxpay.util import deal_with_wx_result

CHANNEL_MAP = {
    2: 'reg_offline',
    6: 'reg_online',
    10: 'dine',
}


@gen.coroutine
def get_wx_configs(wx_sub_id, channel_type=2):
    defaul_err_msg = u"查询微信配置出现未知错误"
    wx_reg_msg = ''
    wx_configs = {}
    jsapi_path_list = None
    appid_config_list = []
    default_subscribe = None
    if wx_sub_id:
        query_args = {
            'sub_mch_id': wx_sub_id
        }
        wx_result = yield query_wx.query_wx_api(query_args, query_type='querysubdevconfig', channel=channel_type)
        if wx_result:
            jsapi_path_list_str, msg = deal_with_wx_result(wx_result, 'jsapi_path_list', defaul_err_msg)
            if jsapi_path_list_str:
                jsapi_path_list_root = json.loads(jsapi_path_list_str)
                if jsapi_path_list_root:
                    jsapi_path_list = jsapi_path_list_root.get('jsapi_path_list')

                appid_config_list_root = json.loads(wx_result.get('appid_config_list', '{}'))
                if appid_config_list_root:
                    appid_configs = appid_config_list_root.get('appid_config_list', '{}')
                    for each_api_config in appid_configs:
                        if each_api_config.get('sub_appid', None) == 'null':
                            default_subscribe = each_api_config.get('subscribe_appid', '')
                        else:
                            appid_config_list.append(each_api_config.get('sub_appid', ''))
            else:
                wx_reg_msg = msg

    # or ['http://baidu.com/', 'http://baidu.com/', 'http://baidu.com/']
    wx_configs['jsapi_path_list'] = jsapi_path_list or []
    # [{'sub_appid':'23123132123123123'},{'sub_appid':'123123123123'}]
    wx_configs['appid_config_list'] = appid_config_list or []
    wx_configs['default_subscribe'] = default_subscribe or ''
    wx_configs['err_msg'] = wx_reg_msg
    wx_configs['channel_type'] = CHANNEL_MAP[channel_type]
    raise gen.Return(wx_configs)


@gen.coroutine
def set_wx_config(params, channle_type):
    wx_result = yield query_wx.query_wx_api(params, query_type='add_appid', channel=channle_type)
    result_code, result_msg = deal_with_wx_result(wx_result)
    raise gen.Return((result_code, result_msg))


@gen.coroutine
def set_channel_config(query_wx_sub_id, channel, config_key, config_value):
    msg = ''
    if config_key == 'jsapi_path':
        is_valid = (config_value.startswith(u'http://') or config_value.startswith(u"https//:")) or re.match(
            '^http(s)://.*', config_value)
        if not is_valid:
            msg = '授权目录必须以http://或https://开头'
        if not config_value.endswith('/'):
            msg = '支付授权目录必须以/结尾'
    if msg:
        raise gen.Return((None, msg))

    config_value_list = list()
    config_value_list.append(config_value)

    for each_config in config_value_list:
        query_args = {
            config_key: each_config,
            'sub_mch_id': query_wx_sub_id
        }
        result_code, result_msg = yield set_wx_config(query_args, channel)
        raise gen.Return((result_code, result_msg))
