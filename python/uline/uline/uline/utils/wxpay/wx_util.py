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

from uline.utils.wxpay import query_wx
from uline.utils.wxpay.util import deal_with_wx_result

CHANNEL_MAP = {
    1: 2,
    2: 6,
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
                            appid_config_list.append(each_api_config)
            else:
                wx_reg_msg = msg

    # or ['http://baidu.com/', 'http://baidu.com/', 'http://baidu.com/']
    wx_configs['jsapi_path_list'] = jsapi_path_list or []
    # [{'sub_appid':'23123132123123123'},{'sub_appid':'123123123123'}]
    wx_configs['appid_config_list'] = appid_config_list or []
    wx_configs['default_subscribe'] = default_subscribe or ''
    wx_configs['wx_msg'] = wx_reg_msg
    wx_configs['channel_type'] = channel_type
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
        raise gen.Return(msg)

    wx_configs = yield get_wx_configs(query_wx_sub_id, channel_type=channel)
    msg = wx_configs.get('wx_msg', '')
    if msg:
        raise gen.Return(msg)

    key_map = {
        'subscribe_appid': 'default_subscribe',
        'sub_appid': 'appid_config_list',
        'jsapi_path': 'jsapi_path_list'
    }

    # 判断是否已经存在
    wx_config_value = wx_configs.get(key_map[config_key])
    if wx_config_value:
        has_exist_msg = u'微信没有提供修改接口，请联系客服人员协助修改相关参数，客服电话：400-804-7555'
        has_exist_path = u'该目录已添加'
        if config_key == u'jsapi_path':
            # 在配置中存在或配置长度等于5
            if config_value in wx_config_value:
                msg = has_exist_path
            if len(wx_config_value) == 5:
                msg = '支付目录已达到最大容量5'
            if msg:
                raise gen.Return(msg)

        if config_key == 'subscribe_appid' and wx_config_value:
            msg = has_exist_msg

        if config_key == 'sub_appid':
            for each_wx_config in wx_config_value:
                if each_wx_config.get('sub_appid', '') == config_value:
                    msg = has_exist_msg
                    break
        if msg:
            raise gen.Return(msg)

    query_args = {
        config_key: config_value,
        'sub_mch_id': query_wx_sub_id
    }
    result_code, result_msg = yield set_wx_config(query_args, channel)
    if not result_code:
        raise gen.Return(result_msg)
