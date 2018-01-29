#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: query_wx.py
# datetime: 2017/5/22 11:55
# description: 请求微信逻辑

import functools
from hashlib import md5

from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from uline_api.util.log import info_log
from uline_api.settings import (
    # 微信千2，线下
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    # 微信千六 线上
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY, WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA,
    # 微信0费率
    WX_0_APPID, WX_0_WX_MCH_ID, WX_0_WXPAY_KEY, WX_0_PRIVATE_KEY, WX_0_PUB_KEY, WX_0_ROOT_CA,
    # 围餐
    WX_DINE_APPID, WX_DINE_WX_MCH_ID, WX_DINE_WXPAY_KEY, WX_DINE_PRIVATE_KEY, WX_DINE_PUB_KEY, WX_DINE_ROOT_CA
)
from .util import dict_to_xml, xml_to_dict

QUERY_KEY_URL = {
    # 商户新进件到微信侧
    'create_mch': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=add',
        'required_keys': ["appid", "mch_id", "merchant_name", "merchant_shortname", "service_phone",
                          "business", "merchant_remark", "channel_id"],
        'any_one_key': [],
        'option_key': ['contact', 'contact_phone', 'contact_email', 'contact_wechatid_type',
                       'contact_wechatid']
    },

    # 修改微信侧商户信息
    'modify_mch': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=modify',
        'required_keys': ["appid", "mch_id", "sub_mch_id", "merchant_shortname", "service_phone"],
        'any_one_key': [],
        'option_key': ["contact"]
    },

    # 获取微信侧商户信息
    'get_mch_info': {
        'url': "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=query",
        'required_keys': ['appid', 'mch_id', 'page_index'],
        'any_one_key': ['merchant_name', 'sub_mch_id'],
        'option_key': ['page_size']
    },

    # 指定渠道号
    'channel_setting': {
        'url': "https://api.mch.weixin.qq.com/secapi/mch/channelsetting",
        'required_keys': ['appid', 'mch_id', 'sub_mch_id', 'channel_id'],
        'any_one_key': [],
        'option_key': []
    },

    # 新增支付配置
    'add_appid': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/addsubdevconfig',
        'required_keys': ['appid', 'mch_id', 'sub_mch_id'],
        'any_one_key': ['jsapi_path', 'sub_appid', 'subscribe_appid'],
        'option_key': []
    },

    # 查询支付配置
    'querysubdevconfig': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/querysubdevconfig',
        'required_keys': ['appid', 'mch_id', 'sub_mch_id'],
        'any_one_key': [],
        'option_key': []
    }
}

# 微信费率通道配置
WX_CERT_CONFIGS = {
    # 微信0费率
    0: {
        'appid': WX_0_APPID,
        'mch_id': WX_0_WX_MCH_ID,
        'wx_key': WX_0_WXPAY_KEY,
        'wx_private_key': WX_0_PRIVATE_KEY,
        'wx_pub_key': WX_0_PUB_KEY,
        'wx_root_ca': WX_0_ROOT_CA
    },
    # 千二费率通道
    2: {
        'appid': APPID,
        'mch_id': WX_MCH_ID,
        'wx_key': WXPAY_KEY,
        'wx_private_key': WX_PRIVATE_KEY,
        'wx_pub_key': WX_PUB_KEY,
        'wx_root_ca': WX_ROOT_CA
    },
    # 千6费率通道
    6: {
        'appid': WX_APP_APPID,
        'mch_id': WX_APP_MCH_ID,
        'wx_key': WXPAY_APP_KEY,
        'wx_private_key': WX_APP_PRIVATE_KEY,
        'wx_pub_key': WX_APP_PUB_KEY,
        'wx_root_ca': WX_APP_ROOT_CA
    },
    # 微信围餐
    10: {
        'appid': WX_DINE_APPID,
        'mch_id': WX_DINE_WX_MCH_ID,
        'wx_key': WX_DINE_WXPAY_KEY,
        'wx_private_key': WX_DINE_PRIVATE_KEY,
        'wx_pub_key': WX_DINE_PUB_KEY,
        'wx_root_ca': WX_DINE_ROOT_CA
    },
}


def wx_sign(params, wxpay_key):
    _temp = sorted(params.items())
    _temp.append(('key', wxpay_key))
    _temp = '&'.join(u'{}={}'.format(key, value) for key, value in _temp)
    sign = md5(_temp.encode('utf-8')).hexdigest().upper()
    return sign


def get_wx_query_params(wx_key, query_args={}):
    """
    :param wx_key: 进行签名时的wx key
    :param query_args: 查询时的参数
    :return: xml内容
    """
    sign = wx_sign(params=query_args, wxpay_key=wx_key)
    query_args['sign'] = sign
    xml = dict_to_xml(query_args)
    return xml


@gen.coroutine
def query_wx(query_url_key, query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    # 判断是否有请求地址
    query_infos = QUERY_KEY_URL.get(query_url_key, {})
    query_url = query_infos.get('url')
    if not query_url:
        raise Exception(u"无效的请求地址")

    # 判断是否缺少必填参数
    required_keys = query_infos.get("required_keys")
    any_one_keys = query_infos.get('any_one_key')
    option_key = query_infos.get('option_key')
    lack_required_key, lack_any_one_key = get_lack_args(query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        info_log.exception("wx_query {} lack required args: {}".format(
            query_url_key, ",".join(lack_required_key)))
        info_log.exception("wx_query {} lack any_one_key args: {}".format(
            query_url_key, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")

    # 处理多余参数
    query_args = deal_excess_key(query_args, required_keys + any_one_keys + option_key)
    # 记录请求的url和参数
    query_params = get_wx_query_params(wx_key, query_args=query_args)
    info_log.info('wx_{},args: {}'.format(query_url_key, query_args))
    info_log.info('wx_{},query_data: {}'.format(query_url_key, query_params))

    # 请求微信侧
    http_client = AsyncHTTPClient()
    try:
        response = yield http_client.fetch(
            query_url,
            method='POST', body=query_params,
            client_key=wx_private_key,
            client_cert=wx_pub_key, ca_certs=wx_root_ca,
            connect_timeout=5, request_timeout=5
        )
        response_data = xml_to_dict(response.body)
        if response_data.get('root'):
            ret = response_data.get('root')
        else:
            ret = response_data.get('xml')
        info_log.info(response.body)
    except:
        ret = {}
    raise gen.Return(ret)


def deal_excess_key(query_args, accept_keys):
    """ 是否有多余的参数
    :param query_args: 请求的字段
    :param accept_keys: 请求能接受的参数
    :return: 去除多余参数的query_args
    """
    for single_key in query_args.keys():
        if single_key not in accept_keys:
            query_args.pop(single_key)
    return query_args


def get_lack_args(query_args, required_keys, any_one_keys):
    """ 是否缺少必填字段或者缺少多项选填一项
    :param query_args: 请求的字段
    :param required_keys: 必填字段
    :param any_one_keys: 多项选填一项
    :return: bool,如果缺少，则为所缺少的参数,否则为[]
    """
    lack_required_key = [each_key for each_key in required_keys if each_key not in query_args]
    lack_any_one_key = []
    for any_one_key in any_one_keys:
        if any_one_key in query_args:
            break
    else:
        lack_any_one_key = any_one_keys
    return lack_required_key, lack_any_one_key


@gen.coroutine
def get_wx_mch_info(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    query_args['page_index'] = '1'
    query_args['page_size'] = '50'
    result = yield query_wx('get_mch_info', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def modify_wx_mch_info(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('modify_mch', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def create_wx_mch(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('create_mch', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def set_mch_channel_id(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('channel_setting', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def add_mch_appid(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('add_appid', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def wx_api(query_args, query_type, appid, mch_id, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    query_args['appid'] = appid
    query_args['mch_id'] = mch_id
    result = yield query_wx(query_type, query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)

# 调用微信api


@gen.coroutine
def query_wx_api(query_args, query_type, channel=2):
    channel_config = WX_CERT_CONFIGS.get(channel, {})
    if not channel_config:
        raise gen.Return(False)
    partial_func = functools.partial(wx_api, **channel_config)
    result = yield partial_func(query_args, query_type)
    raise gen.Return(result)


# 商户新进件到微信侧
create_wx_mch_common = functools.partial(wx_api,
                                         query_type='create_mch',
                                         appid=APPID,
                                         mch_id=WX_MCH_ID,
                                         wx_key=WXPAY_KEY,
                                         wx_private_key=WX_PRIVATE_KEY,
                                         wx_pub_key=WX_PUB_KEY, wx_root_ca=WX_ROOT_CA)

# 商户新进件到微信侧(微信app)
create_wx_mch_wx_app = functools.partial(wx_api,
                                         query_type='create_mch',
                                         appid=WX_APP_APPID,
                                         mch_id=WX_APP_MCH_ID,
                                         wx_key=WXPAY_APP_KEY,
                                         wx_private_key=WX_APP_PRIVATE_KEY,
                                         wx_pub_key=WX_APP_PUB_KEY, wx_root_ca=WX_APP_ROOT_CA)

# 修改微信侧商户信息
modify_wx_mch_info_common = functools.partial(wx_api,
                                              query_type='modify_mch',
                                              appid=APPID,
                                              mch_id=WX_MCH_ID,
                                              wx_key=WXPAY_KEY,
                                              wx_private_key=WX_PRIVATE_KEY,
                                              wx_pub_key=WX_PUB_KEY, wx_root_ca=WX_ROOT_CA)

# 修改微信侧商户信息(微信app)
modify_wx_mch_info_wx_app = functools.partial(wx_api,
                                              query_type='modify_mch',
                                              appid=WX_APP_APPID,
                                              mch_id=WX_APP_MCH_ID,
                                              wx_key=WXPAY_APP_KEY,
                                              wx_private_key=WX_APP_PRIVATE_KEY,
                                              wx_pub_key=WX_APP_PUB_KEY, wx_root_ca=WX_APP_ROOT_CA)

# 获取微信侧商户信息
get_wx_mch_info_common = functools.partial(wx_api,
                                           query_type='get_mch_info',
                                           appid=APPID,
                                           mch_id=WX_MCH_ID,
                                           wx_key=WXPAY_KEY,
                                           wx_private_key=WX_PRIVATE_KEY,
                                           wx_pub_key=WX_PUB_KEY, wx_root_ca=WX_ROOT_CA)

# 获取微信侧商户信息(微信app)
get_wx_mch_info_wx_app = functools.partial(wx_api,
                                           query_type='get_mch_info',
                                           appid=WX_APP_APPID,
                                           mch_id=WX_APP_MCH_ID,
                                           wx_key=WXPAY_APP_KEY,
                                           wx_private_key=WX_APP_PRIVATE_KEY,
                                           wx_pub_key=WX_APP_PUB_KEY, wx_root_ca=WX_APP_ROOT_CA)

# # 新增支付配置
add_mch_appid_common = functools.partial(wx_api,
                                         query_type='add_appid',
                                         appid=APPID,
                                         mch_id=WX_MCH_ID,
                                         wx_key=WXPAY_KEY,
                                         wx_private_key=WX_PRIVATE_KEY,
                                         wx_pub_key=WX_PUB_KEY, wx_root_ca=WX_ROOT_CA)

# 新增支付配置(微信app)
add_mch_appid_wx_app = functools.partial(wx_api,
                                         query_type='add_appid',
                                         appid=WX_APP_APPID,
                                         mch_id=WX_APP_MCH_ID,
                                         wx_key=WXPAY_APP_KEY,
                                         wx_private_key=WX_APP_PRIVATE_KEY,
                                         wx_pub_key=WX_APP_PUB_KEY, wx_root_ca=WX_APP_ROOT_CA)

# 指定渠道号
set_mch_channel_id_common = functools.partial(wx_api,
                                              query_type='channel_setting',
                                              appid=APPID,
                                              mch_id=WX_MCH_ID,
                                              wx_key=WXPAY_KEY,
                                              wx_private_key=WX_PRIVATE_KEY,
                                              wx_pub_key=WX_PUB_KEY, wx_root_ca=WX_ROOT_CA)

# 指定渠道号(微信app)
set_mch_channel_id_wx_app = functools.partial(wx_api,
                                              query_type='channel_setting',
                                              appid=WX_APP_APPID,
                                              mch_id=WX_APP_MCH_ID,
                                              wx_key=WXPAY_APP_KEY,
                                              wx_private_key=WX_APP_PRIVATE_KEY,
                                              wx_pub_key=WX_APP_PUB_KEY, wx_root_ca=WX_APP_ROOT_CA)

# 查询支付配置
query_mch_config_common = functools.partial(query_wx_api, query_type='querysubdevconfig')

query_mch_config_wx_app = functools.partial(query_wx_api, query_type='querysubdevconfig', channel=6)
