#!/usr/bin/env python
# -*- coding: utf-8 -*-

RETURN_MSG = {
    'success': {
        'code': 10000,
        'msg': "SUCCESS",
        'error_msg': "",
    },

    'params_error': {
        'code': 10001,
        'msg': "FAIL",
        'error_msg': "参数错误",
    },

    'unkown_error': {
        'code': 10110,
        'msg': "FAIL",
        'error_msg': "未知错误",
    },

    'no_merchant': {
        'code': 20000,
        'msg': "FAIL",
        'error_msg': "无相关商户信息"
    },

    'logic_error': {
        'code': 110000,
        'msg': "FAIL",
        'error_msg': "出现逻辑错误",
    },

    # 交易风险相关
    'no_deal_plan': {
       "code": 30001,
       "msg": "FAIL",
       "error_msg": "请选择处理方案",
    },

    "no_trade_info": {
        "code": 30002,
        "msg": "FAIL",
        "error_msg": "无此风险信息",
    },

    "no_merchant_info": {
        "code": 30003,
        "msg": "FAIL",
        "error_msg": "无对应有效商户",
    },

    "no_platform": {
        "code": 30004,
        "msg": "FAIL",
        "error_msg": "无对应平台信息"
    },
}
