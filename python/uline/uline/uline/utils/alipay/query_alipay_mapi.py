#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import json

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPClient

from new_merchantInletToAlipay import query_mapi_info
from uline.public import log
from uline.settings import ALI_APPID, ALI_PID, ALI_PRIVATE_KEY, ALI_PUB_KEY, ALI_SERVER_ADDRESS
from uline import settings

QUERY_KEY_URL = {
    # 商户风险信息查询
    'customerrisk_query': {
        'url': settings.ALI_RISK_SERVER_ADDRESS,
        'method': 'alipay.security.risk.customerrisk.query',
        'any_one_key': [],
        'option_key': ['cert_no', 'bank_card_no', 'external_id', 'business_license_no'],
        'required_keys': ['risk_type']
    },

    'customerrisk_send': {
        'url': settings.ALI_RISK_SERVER_ADDRESS,
        'method': 'alipay.security.risk.customerrisk.send',
        'any_one_key': [],
        'option_key': ['business_license_no', 'bank_card_no', 'cert_no', 'external_id'],
        'required_keys': ['smid', 'process_code']
    }
}

ALI_CONFIGS = {
    'default': {
        'appid': ALI_APPID,
        'pid': ALI_PID,
        'private_key_file': ALI_PRIVATE_KEY,
        'pub_key_file': ALI_PUB_KEY,
    },
    'risk': {
        'app_id': settings.ALI_RISK_APPID,
        'pid': settings.ALI_RISK_PID,
        'private_key_file': settings.ALI_RISK_PRIVATE_KEY,
        'pub_key_file': settings.ALI_RISK_PUB_KEY,
    }
}


@gen.coroutine
def _query_ali_mapi(query_method, query_args, config_info, requred_param_key='required_keys',
                    crypto_type='RSA', http_method='GET', charset='UTF-8'):
    query_infos = QUERY_KEY_URL.get(query_method)

    method = query_infos.get('method')

    # 判断是否缺少必填参数
    any_one_keys = query_infos.get('any_one_key')
    # any_one_keys = []
    option_key = query_infos.get('option_key')

    required_keys = query_infos.get(requred_param_key)

    lack_required_key, lack_any_one_key = get_lack_args(query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        log.detail.exception("alipay_query {} lack required args: {}".format(query_method, ",".join(lack_required_key)))
        log.detail.exception(
            "alipay_query {} lack any_one_key args: {}".format(query_method, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")
    # 处理多余参数
    query_args = deal_excess_key(query_args, required_keys + any_one_keys + option_key)
    server_address = query_infos.get('url', '')
    # 记录请求的url和参数
    query_args = {key: query_args[key] for key in sorted(query_args)}
    query_params, sign = query_mapi_info(method, query_args, config_info, crypto_type, charset)
    log.detail.info('alipay_{},args: {}'.format(query_method, query_args))
    log.detail.info('alipay_{},ALIPAY_URL:{},query_data: {}'.format(query_method, server_address, query_params))

    # 请求支付宝
    http_client = AsyncHTTPClient()
    query_configs = {
        'method': http_method,
    }
    query_url = server_address
    if http_method == "GET":
        query_url = server_address + '?{}'.format(query_params)
    elif http_method == "POST":
        query_configs['body'] = query_params

    response = yield http_client.fetch(query_url, **query_configs)
    try:
        ret = json.loads(response.body.decode(charset))
        log.detail.info(response.body.decode(charset))
        ali_ret = ret.get('%s_response' % method.replace('.', '_'))
    except Exception as e:
        log.detail.exception(e)
        ali_ret = {}
    raise gen.Return(ali_ret)


def _query_ali_mapi_block(query_method, query_args, config_info, requred_param_key='required_keys',
                          crypto_type='RSA', http_method='GET', charset='UTF-8'):
    query_infos = QUERY_KEY_URL.get(query_method)

    method = query_infos.get('method')

    # 判断是否缺少必填参数
    any_one_keys = query_infos.get('any_one_key')
    # any_one_keys = []
    option_key = query_infos.get('option_key')

    required_keys = query_infos.get(requred_param_key)

    lack_required_key, lack_any_one_key = get_lack_args(query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        log.detail.exception("alipay_query {} lack required args: {}".format(query_method, ",".join(lack_required_key)))
        log.detail.exception(
            "alipay_query {} lack any_one_key args: {}".format(query_method, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")
    # 处理多余参数
    query_args = deal_excess_key(query_args, required_keys + any_one_keys + option_key)
    server_address = query_infos.get('url', '')
    # 记录请求的url和参数
    query_args = {key: query_args[key] for key in sorted(query_args)}
    query_params, sign = query_mapi_info(method, query_args, config_info, crypto_type, charset)
    log.detail.info('alipay_{},args: {}'.format(query_method, query_args))
    log.detail.info('alipay_{},ALIPAY_URL:{},query_data: {}'.format(query_method, server_address, query_params))

    # 请求支付宝
    http_client = HTTPClient()
    query_configs = {
        'method': http_method,
    }
    query_url = server_address
    if http_method == "GET":
        query_url = server_address + '?{}'.format(query_params)
    elif http_method == "POST":
        query_configs['body'] = query_params

    response = http_client.fetch(query_url, **query_configs)
    try:
        ret = json.loads(response.body.decode(charset))
        log.detail.info(response.body.decode(charset))
        ali_ret = ret.get('%s_response' % method.replace('.', '_'))
    except Exception as e:
        log.detail.exception(e)
        ali_ret = {}
    return ali_ret


def get_lack_args(query_args, required_keys=[], any_one_keys=[]):
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


@gen.coroutine
def query_ali_mapi(query_method, query_args, channel, requred_param_key='required_keys', crypto_type='RSA',
                   http_method='GET', charset='UTF-8'):
    if query_method not in QUERY_KEY_URL.keys():
        raise Exception('Invalid interface')
    channel_config = ALI_CONFIGS.get(channel, None)
    if not channel_config:
        raise Exception("invalid channel")

    result = yield _query_ali_mapi(query_method, query_args, channel_config, requred_param_key, crypto_type,
                                   charset=charset, http_method=http_method)
    raise gen.Return(result)


def query_ali_mapi_block(query_method, query_args, channel, requred_param_key='required_keys', crypto_type='RSA',
                         http_method='GET', charset='UTF-8'):
    if query_method not in QUERY_KEY_URL.keys():
        raise Exception('Invalid interface')
    channel_config = ALI_CONFIGS.get(channel, None)
    if not channel_config:
        raise Exception("invalid channel")

    result = _query_ali_mapi_block(query_method, query_args, channel_config, requred_param_key, crypto_type,
                                   charset=charset, http_method=http_method)
    return result
