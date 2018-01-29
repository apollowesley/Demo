#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: guozhihua
# contact: guozhihua@ulaiber.com
# filename: query_weixin.py
# datetime: 2017/06/14
# description: 请求支付宝逻辑

import functools
import json

from new_merchantInletToAlipay import mch_inlet_to_alipay_data, mch_inlet_to_alipay_data_block
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPClient

from uline_risk.settings import ALI_APPID, ALI_PID, ALI_PRIVATE_KEY, ALI_PUB_KEY, ALI_SERVER_ADDRESS
from uline_risk.utils import log

# 支付宝分级商户入驻接入指南
# https://doc.open.alipay.com/docs/doc.htm?docType=1&articleId=106509

# ALIPAY_URL = 'https://openapi.alipay.com/gateway.do'

PUBLIC_REQUIER_KEYS = ['app_id', 'method', 'format', 'charset', 'sign_type', 'sign', 'timestamp', 'version',
                       'notify_url', 'biz_content']

PUBLIC_OPTION_KEYS = ['format', 'notify_url', 'app_auth_token']

INTERFACE_BASE_KEYS = ['external_id', 'name', 'alias_name', 'service_phone', 'category_id', 'source']

QUERY_KEY_URL = {
    # 间连分级商户入驻
    'indirect_create': {
        'url': ALI_SERVER_ADDRESS,
        'method': 'ant.merchant.expand.indirect.create',
        'any_one_key': [],
        'option_key': [],
        'M0': [],
        'M1': INTERFACE_BASE_KEYS,
        'M2': INTERFACE_BASE_KEYS + ['address_info'],
        'M3': INTERFACE_BASE_KEYS + ['business_license', 'business_license_type', 'contact_info',
                                     'address_info', 'bankcard_info']
    },
    # 间连分级商户查询接口
    'indirect_query': {
        'url': ALI_SERVER_ADDRESS,
        'method': 'ant.merchant.expand.indirect.query',
        'any_one_key': ['external_id', 'sub_merchant_id'],
        'option_key': [],
    },
    # 间连分级商户修改接口
    'indirect_modify': {
        'url': ALI_SERVER_ADDRESS,
        'method': 'ant.merchant.expand.indirect.modify',
        'any_one_key': [],
        'option_key': [],
        'M0': [],
        'M1': INTERFACE_BASE_KEYS,
        'M2': INTERFACE_BASE_KEYS + ['address_info'],
        'M3': INTERFACE_BASE_KEYS + ['business_license', 'business_license_type', 'contact_info',
                                     'address_info', 'bankcard_info']
    }

}

ALI_CONFIGS = {
    'default': {
        'appid': ALI_APPID,
        'pid': ALI_PID,
        'private_key': ALI_PRIVATE_KEY,
        'pub_key': ALI_PUB_KEY,
        'server_address': ALI_SERVER_ADDRESS
    }
}


@gen.coroutine
def query_ali(query_type, level, query_args, appid, pid, private_key, pub_key, server_address):
    query_infos = QUERY_KEY_URL.get(query_type)

    method = query_infos.get('method')

    # 判断是否缺少必填参数
    required_keys = []
    # any_one_keys = query_infos.get('any_one_key')
    any_one_keys = []
    # option_key = query_infos.get('option_key')

    # 如果是新增、修改，需判断商户等级
    if query_type in ['indirect_create', 'indirect_modify']:
        required_keys = query_infos.get(level)

    lack_required_key, lack_any_one_key = get_lack_args(query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        log.detail.exception("alipay_query {} lack required args: {}".format(
            query_type, ",".join(lack_required_key)))
        log.detail.exception("alipay_query {} lack any_one_key args: {}".format(
            query_type, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")

    # 处理多余参数
    # query_args = deal_excess_key(query_args, required_keys + any_one_keys + option_key)
    # 记录请求的url和参数
    query_params = yield mch_inlet_to_alipay_data(query_args, method)
    log.detail.info('alipay_{},args: {}'.format(query_type, query_args))
    log.detail.info('alipay_{},ALIPAY_URL:{},query_data: {}'.format(
        query_type, ALI_SERVER_ADDRESS, query_params))

    # 请求支付宝
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(
        ALI_SERVER_ADDRESS,
        method='POST', body=query_params,
    )
    try:
        ret = json.loads(response.body.decode('gbk'))
        log.detail.info(response.body.decode('gbk'))
        ali_ret = ret.get('%s_response' % method.replace('.', '_'))
    except Exception:
        ali_ret = {}
    raise gen.Return(ali_ret)


def query_ali_block(query_type, level, query_args, appid, pid, private_key, pub_key, server_address):
    query_infos = QUERY_KEY_URL.get(query_type)

    method = query_infos.get('method')

    # 判断是否缺少必填参数
    required_keys = []
    # any_one_keys = query_infos.get('any_one_key')
    any_one_keys = []
    # option_key = query_infos.get('option_key')
    # option_key = []

    # 如果是新增、修改，需判断商户等级
    if query_type in ['indirect_create', 'indirect_modify']:
        required_keys = query_infos.get(level)

    lack_required_key, lack_any_one_key = get_lack_args(query_args, required_keys, any_one_keys)
    if lack_required_key or lack_any_one_key:
        log.detail.exception("alipay_query {} lack required args: {}".format(
            query_type, ",".join(lack_required_key)))
        log.detail.exception("alipay_query {} lack any_one_key args: {}".format(
            query_type, ",".join(lack_any_one_key)))
        raise Exception(u"缺少请求参数")

    # 处理多余参数
    # query_args = deal_excess_key(query_args, required_keys + any_one_keys + option_key)
    # 记录请求的url和参数
    query_params = mch_inlet_to_alipay_data_block(query_args, method)
    log.detail.info('alipay_{},args: {}'.format(query_type, query_args))
    log.detail.info('alipay_{},ALIPAY_URL:{},query_data: {}'.format(
        query_type, ALI_SERVER_ADDRESS, query_params))

    # 请求支付宝
    http_client = HTTPClient()
    response = http_client.fetch(ALI_SERVER_ADDRESS, method='POST', body=query_params)
    ret = json.loads(response.body.decode('gbk'))
    log.detail.info(response.body.decode('gbk'))
    ali_ret = ret.get('%s_response' % method.replace('.', '_'))
    return ali_ret


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


@gen.coroutine
def ali_api(query_args, query_type, appid, pid, private_key, pub_key, server_address, level='M2'):
    if query_type not in QUERY_KEY_URL.keys():
        raise gen.Return('Invalid interface')
    query_args['source'] = pid
    result = yield query_ali(query_type, level, query_args, appid, pid, private_key, pub_key, server_address)
    raise gen.Return(result)


def ali_api_block(query_args, query_type, channel='default', level='M2'):
    if query_type not in QUERY_KEY_URL.keys():
        return 'Invalid interface'
    channel_config = ALI_CONFIGS.get(channel, {})
    if not channel_config:
        return False
    query_args['source'] = channel_config['pid']
    partial_func = functools.partial(query_ali_block, **channel_config)
    result = partial_func(query_type, level, query_args)
    return result


# 商户新进件到支付宝
create_alipay_mch_common = functools.partial(ali_api,
                                             query_type='indirect_create',
                                             appid=ALI_APPID,
                                             pid=ALI_PID,
                                             private_key=ALI_PRIVATE_KEY,
                                             pub_key=ALI_PUB_KEY,
                                             server_address=ALI_SERVER_ADDRESS)

# 商户新进件到支付宝
create_alipay_mch_common_m1 = functools.partial(ali_api,
                                                query_type='indirect_create',
                                                appid=ALI_APPID,
                                                pid=ALI_PID,
                                                private_key=ALI_PRIVATE_KEY,
                                                pub_key=ALI_PUB_KEY,
                                                server_address=ALI_SERVER_ADDRESS,
                                                level='M1')

# 支付宝商户查询接口
query_alipay_mch_common = functools.partial(ali_api,
                                            query_type='indirect_query',
                                            appid=ALI_APPID,
                                            pid=ALI_PID,
                                            private_key=ALI_PRIVATE_KEY,
                                            pub_key=ALI_PUB_KEY,
                                            server_address=ALI_SERVER_ADDRESS)

# 支付宝商户修改接口
update_alipay_mch_common = functools.partial(ali_api,
                                             query_type='indirect_modify',
                                             appid=ALI_APPID,
                                             pid=ALI_PID,
                                             private_key=ALI_PRIVATE_KEY,
                                             pub_key=ALI_PUB_KEY,
                                             server_address=ALI_SERVER_ADDRESS)
