#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/30/16'
import decimal
from datetime import datetime, date
import tornado
import tornado.escape
import json
import bcrypt
import tornado.gen
import concurrent.futures
# import datetime


def tojson(data, default=False, **kwargs):
    def serializable(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError

    _default = serializable if default else None
    return json.dumps(data,
                      default=_default,
                      separators=(',', ':'),
                      **kwargs).replace("</", "<\\/")


executor = concurrent.futures.ThreadPoolExecutor(2)


@tornado.gen.coroutine
def bcrypt_pwd(pwd, validate=None):
    # 使用bcrypt生成安全的密码,且支持验证
    if not validate:
        hashed_password = yield executor.submit(
            bcrypt.hashpw,
            tornado.escape.utf8(pwd),
            bcrypt.gensalt()
        )
        raise tornado.gen.Return(hashed_password)
    else:
        hashed_password = yield executor.submit(
            bcrypt.hashpw,
            tornado.escape.utf8(pwd),
            tornado.escape.utf8(validate)
        )
        raise tornado.gen.Return(hashed_password == validate)


def default_parse(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    else:
        return str(obj)