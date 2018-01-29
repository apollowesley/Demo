#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json

from tornado.httpclient import AsyncHTTPClient, HTTPClient
from tornado import gen

from uline.settings import RISK_API_URL
from uline.public import log

base_url = RISK_API_URL

RISK_API_MAP = {
    "merchant_risk_list": {
        "path": "/merchant_risk/",
    },
    "trade_risk_list": {
        "path": "/trade_risk/",
    },
    "merchant_settle_setting": {
        "path": "/merchant/settle/deal",
    },
    "merchant_credit_setting": {
        "path": "/merchant/credit/deal",
    },
    "alipay_trade_risk_notify": {
        "path": "/trade_risk/alipay",
    },
    "alipay_trade_risk_deal": {
        "path": "/trade_risk/deal",
    },
    "alipay_merchant_risk_add": {
        "path": "/merchant_risk/add/alipay",
    }
}


@gen.coroutine
def query_risk_api(api_name, method="GET", params=None, body=None, **kwargs):
    url_config = RISK_API_MAP.get(api_name, None)
    if not url_config:
        raise Exception("没有对应api")
    path = url_config.get("path", "")
    query_url = "{}{}".format(base_url, path)
    http_client = AsyncHTTPClient()

    response = None
    if method.upper() == "GET":
        query = ""
        if isinstance(params, dict):
            query = urllib.urlencode(params)
        elif isinstance(params, str):
            query = params
        if query:
            query_url = "{}?{}".format(query_url, query)
    if method.upper() == "POST":
        if isinstance(body, dict):
            body = json.dumps(body)
    log.exception.info("query risk api, query_url:{}, method:{},body:{}".format(query_url, method, body))
    response = yield http_client.fetch(query_url, method=method, body=body, **kwargs)
    response_code = response.code
    result = {"code": 20000, "error_msg": '未知错误'}
    if response and response_code == 200 and response.body:
        result = json.loads(response.body)
        log.exception.info("query risk api result:{}".format(result))
    elif response and response_code != 200:
        log.exception.info("query riks result, code:{}, reason:{}".format(response_code, response.reason))
        result['error_msg'] = response.reason
    raise gen.Return(result)


def query_risk_api_block(api_name, method="GET", params=None, body=None, **kwargs):
    url_config = RISK_API_MAP.get(api_name, None)
    if not url_config:
        raise Exception("没有对应api")
    path = url_config.get("path", "")
    query_url = "{}{}".format(base_url, path)
    http_client = HTTPClient()

    response = None
    if method.upper() == "GET":
        query = ""
        if isinstance(params, dict):
            query = urllib.urlencode(params)
        elif isinstance(params, str):
            query = params
        if query:
            query_url = "{}?{}".format(query_url, query)
    if method.upper() == "POST":
        if isinstance(body, dict):
            body = json.dumps(body)
    log.exception.info("query risk api, query_url:{}, method:{},body:{}".format(query_url, method, body))
    response = http_client.fetch(query_url, method=method, body=body, **kwargs)
    response_code = response.code
    result = {"code": 20000, "error_msg": '未知错误'}
    if response and response_code == 200 and response.body:
        result = json.loads(response.body)
        log.exception.info("query risk api result:{}".format(result))
    elif response and response_code != 200:
        log.exception.info("query riks result, code:{}, reason:{}".format(response_code, response.reason))
        result['error_msg'] = response.reason
    return result


def check_response(result):
    code = result.get('code', 2000)
    is_success, message = True, "SUCCESS"
    if code != 10000:
        is_success = False
        message = result.get("error_msg", '未知错误')
    return is_success, message
