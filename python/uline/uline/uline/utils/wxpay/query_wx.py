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
import copy

import requests
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPClient

from uline.public import log
from uline.settings import (
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
    },

    # 图片上传API_变更文档
    # 返回结果:<xml>
    # <return_code><![CDATA[SUCCESS]]></return_code>
    # <return_msg><![CDATA[OK]]></return_msg>
    # <result_code><![CDATA[SUCCESS]]></result_code>
    # <media_id><![CDATA[MZPUO0HONxwyvQafQt5EOK9ekt0x-V3HJfJMC-FeSc-vySuJD630AhQr_YU_nYDxnQ38PMaYU9dqRQS775YRdZ_S2iFsSuCpznqwBv0qcrI]]></media_id>
    # <sign><![CDATA[761CA82B0C7542C81ADD9D436C549992]]></sign>
    # </xml>
    'uploadpicturesapi': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/uploadmedia',
        'required_keys': ['media', 'mch_id', 'media_hash'],
        'any_one_key': [],
        'option_key': [],
        'sign_except': ['media']
    },

    # 服务商操作员调用API添加门店(API变更)
    # 返回结果示例:
    # <xml><return_code><![CDATA[SUCCESS]]></return_code>
    # <return_msg><![CDATA[OK]]></return_msg>
    # <result_code><![CDATA[SUCCESS]]></result_code>
    # <mch_id><![CDATA[1483783812]]></mch_id>
    # <sub_mch_id><![CDATA[36979256]]></sub_mch_id>
    # <shop_id><![CDATA[1200106692]]></shop_id>
    # </xml>
    'greenplangetnewcs': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/addoasisstore',
        'required_keys': ['sub_mch_id', 'mch_id', 'shop_name', 'shop_address_code', 'shop_street', 'shop_entrance_pic',
                          'checkstand_pic', 'business_license_pic', 'indoor_pic', 'nonce_str'],
        'any_one_key': [],
        'option_key': []
    },

    # API变更：门店被驳回后，修改门店信息API（新增）适用于绿洲计划修改被驳回的门店申请单
    'modifycsprofil': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/modifyoasisstore',
        'required_keys': ['sub_mch_id', 'mch_id', 'shop_id', 'shop_name', 'shop_address_code', 'shop_street',
                          'shop_entrance_pic', 'checkstand_pic', 'business_license_pic', 'indoor_pic', 'nonce_str'],
        'any_one_key': [],
        'option_key': []
    },
    # 变更API：查询当前门店审核结果（新增）适用于查询绿洲计划门店申请单的状态
    'queryauthresult': {
        'url': 'https://api.mch.weixin.qq.com/secapi/mch/getoasisstore',
        'required_keys': ['sub_mch_id', 'mch_id', 'shop_id', 'nonce_str'],
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


def get_wx_query_params(wx_key, query_args={}, sign_except_keys=[]):
    """
    :param wx_key: 进行签名时的wx key
    :param query_args: 查询时的参数
    :param sign_except_keys: 签名时排除的参数
    :return: xml内容
    """
    sign_infos = {key: query_args[key] for key in query_args if key not in sign_except_keys}
    sign = wx_sign(params=sign_infos, wxpay_key=wx_key)
    query_args['sign'] = sign


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
    sign_exceptkey = query_infos.get('sign_except', [])
    lack_required_key, lack_any_one_key = get_lack_args(
        query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        log.detail.exception("wx_query {} lack required args: {}".format(
            query_url_key, ",".join(lack_required_key)))
        log.detail.exception("wx_query {} lack any_one_key args: {}".format(
            query_url_key, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")

    # 处理多余参数
    query_args = deal_excess_key(
        query_args, required_keys + any_one_keys + option_key)
    # 记录请求的url和参数
    get_wx_query_params(wx_key, query_args=query_args, sign_except_keys=sign_exceptkey)
    query_params = dict_to_xml(query_args)
    log.detail.info('wx_{},args: {}'.format(query_url_key, query_args))
    log.detail.info('wx_{},query_data: {}'.format(query_url_key, query_params))

    # 请求微信侧
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(
        query_url,
        method='POST', body=query_params,
        client_key=wx_private_key,
        client_cert=wx_pub_key, ca_certs=wx_root_ca
    )
    response_data = xml_to_dict(response.body)
    if response_data.get('root'):
        ret = response_data.get('root')
    else:
        ret = response_data.get('xml')
    log.detail.info(response.body)
    raise gen.Return(ret)


def query_wx_block(query_url_key, query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    # 判断是否有请求地址
    query_infos, query_url = check_query_url(query_url_key)
    # 判断是否缺少必填参数
    required_keys = query_infos.get("required_keys",[])
    any_one_keys = query_infos.get('any_one_key')
    option_key = query_infos.get('option_key')
    lack_required_key, lack_any_one_key = get_lack_args(query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        log.detail.exception("wx_query {} lack required args: {}".format(
            query_url_key, ",".join(lack_required_key)))
        log.detail.exception("wx_query {} lack any_one_key args: {}".format(
            query_url_key, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")

    # 处理多余参数
    query_args = deal_excess_key(query_args, required_keys + any_one_keys + option_key)
    # 记录请求的url和参数
    get_wx_query_params(wx_key, query_args=query_args)
    query_params = dict_to_xml(query_args)
    log.detail.info('wx_{},args: {}'.format(query_url_key, query_args))
    log.detail.info('wx_{},query_data: {}'.format(query_url_key, query_params))

    # 请求微信侧
    cert = (wx_pub_key,  wx_private_key)
    response = requests.post(query_url, data=query_params, cert=cert, verify=wx_root_ca, headers={'Connection':'close'})
    response_data = xml_to_dict(response.text)
    if response_data.get('root'):
        ret = response_data.get('root')
    else:
        ret = response_data.get('xml')
    log.detail.info(response.text)
    return ret


def check_query_url(query_url_key):
    query_infos = QUERY_KEY_URL.get(query_url_key, {})
    query_url = query_infos.get('url')
    if not query_url:
        raise Exception(u"无效的请求地址")

    return query_infos, query_url


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
    lack_required_key = [
        each_key for each_key in required_keys if each_key not in query_args]
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
def upload_pic(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('uploadpicturesapi', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def green_plan_get_new_cs(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('greenplangetnewcs', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def modify_cs_profile(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('modifycsprofil', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def query_auth_result(query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    result = yield query_wx('queryauthresult', query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


@gen.coroutine
def wx_api(query_args, query_type, appid, mch_id, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    query_args['appid'] = appid
    query_args['mch_id'] = mch_id
    result = yield query_wx(query_type, query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    raise gen.Return(result)


def wx_api_block(query_args, query_type, appid, mch_id, wx_key, wx_private_key, wx_pub_key, wx_root_ca):
    query_args['appid'] = appid
    query_args['mch_id'] = mch_id
    result = query_wx_block(query_type, query_args, wx_key, wx_private_key, wx_pub_key, wx_root_ca)
    return result


# 调用微信api
@gen.coroutine
def query_wx_api(query_args, query_type, channel=2):
    channel_config = WX_CERT_CONFIGS.get(channel, {})
    if not channel_config:
        raise gen.Return(False)
    partial_func = functools.partial(wx_api, **channel_config)
    result = yield partial_func(query_args, query_type)
    raise gen.Return(result)


def query_wx_api_block(query_args, query_type, channel=2):
    channel_config = WX_CERT_CONFIGS.get(channel, {})
    if not channel_config:
        return False
    partial_func = functools.partial(wx_api_block, **channel_config)
    result = partial_func(query_args, query_type)
    return result


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
query_mch_config_common = functools.partial(
    query_wx_api, query_type='querysubdevconfig')

query_mch_config_wx_app = functools.partial(
    query_wx_api, query_type='querysubdevconfig', channel=6)


def query_wx_use_form(query_args, query_type, need_config_keys=None, files=None, channel=10, ):
    channel_config = WX_CERT_CONFIGS.get(channel, {})
    if not channel_config:
        raise gen.Return(False)
    if need_config_keys:
        query_args.update({key: channel_config.get(key) for key in need_config_keys})
    cert = (channel_config.get('wx_pub_key'), channel_config.get('wx_private_key'))
    wx_key = channel_config.get('wx_key')
    verify = channel_config.get('wx_root_ca')
    result = query_wx_form(query_type, query_args, cert, files, wx_key, verify)
    return result


def get_content_type(filename):
    import mimetypes

    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def query_wx_form(query_url_key, query_args, cert, files, wx_key, verify):
    # 判断是否有请求地址
    query_infos, query_url = check_query_url(query_url_key)
    get_wx_query_params(wx_key, query_args=query_args)

    log.detail.info('wx_{},args: {}'.format(query_url_key, query_args))
    log.detail.info('wx_{},query_data: {}'.format(query_url_key, query_args))

    # 请求微信侧
    response = requests.post(query_url, data=query_args, cert=cert, verify=verify, files=files)
    response_data = xml_to_dict(response.text)
    if response_data.get('root'):
        ret = response_data.get('root')
    else:
        ret = response_data.get('xml')
    log.detail.info(response.text)
    return ret
