#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from copy import deepcopy

from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient

from uline.settings import MESSAGE_URL, MCH_LOGIN_URL, CHAIN_LOGIN_URL

ACTIVE_MCH_TEMPLATE = u"""
{mch_name}，您好：
以下帐号重要信息请注意保密：
商户编号：{mch_id}
登录帐号：{login_name}
初始登录密码：开户时填写的联系手机号 (登录后要求修改初始密码)
初始密钥：{mch_pay_key}
登陆地址：{login_url}
温馨提示：
请妥善保管您的账号及密码，为安全起见，新申请的账号，首次登录后请立即修改管理员密码.

广州优畅信息技术有限公司{addition_info}
客服电话：4008047555"""

ACTIVE_CHAIN_TEMPLATE = u"""
{chain_name}，您好：
以下帐号重要信息请注意保密：
优畅技术文档：http://docs.uline.cc
连锁商户编号：{chain_id}
登录帐号：{login_name}
初始登录密码：开户时填写的联系手机号 (登录后要求修改初始密码)
登陆地址：{login_url}
温馨提示：
请妥善保管您的账号及密码，为安全起见，新申请的账号，首次登录后请立即修改管理员密码.

广州优畅信息技术有限公司{addition_info}
客服电话：4008047555"""

ACTIVE_CS_TEMPLATE = """
{mch_name}，您好：
以下帐号重要信息请注意保密：
门店编号：{mch_id}
初始密钥：{mch_pay_key}

广州优畅信息技术有限公司{addition_info}
客服电话：4008047555"""


@coroutine
def send_active_mch_email(env, mch_info):
    addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''

    receiver_info = deepcopy(mch_info)
    receiver_info['login_url'] = MCH_LOGIN_URL
    receiver_info['addition_info'] = addition_info
    data = {
        'env': env,
        'reciver': receiver_info['email'],
        'title': u'uline商户激活信息',
        'body': ACTIVE_MCH_TEMPLATE.format(**receiver_info)
    }
    response = yield send_email(data)
    raise Return(response)


@coroutine
def send_email(data):
    http_client = AsyncHTTPClient()
    url = MESSAGE_URL + '/v1/email'
    response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
    raise Return(response)


@coroutine
def send_active_chain_email(env, chain_info):
    addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
    receiver_info = deepcopy(chain_info)
    receiver_info['login_url'] = CHAIN_LOGIN_URL
    receiver_info['addition_info'] = addition_info
    data = {
        'env': env,
        'reciver': receiver_info['email'],
        'title': u'uline连锁商户激活信息',
        'body': ACTIVE_CHAIN_TEMPLATE.format(**receiver_info)
    }
    response = yield send_email(data)
    raise Return(response)


@coroutine
def send_active_cs_email(env, mch_info):
    addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''

    receiver_info = deepcopy(mch_info)
    # receiver_info['login_url'] = MCH_LOGIN_URL
    receiver_info['addition_info'] = addition_info
    data = {
        'env': env,
        'reciver': receiver_info['email'],
        'title': u'uline连锁门店激活信息',
        'body': ACTIVE_CS_TEMPLATE.format(**receiver_info)
    }
    response = yield send_email(data)
    raise Return(response)
