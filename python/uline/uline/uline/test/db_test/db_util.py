#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/13/16'

import random
import os
import codecs
import bcrypt
from datetime import datetime, timedelta


def random_timestramp():
    # 生成2016年到现在的随机时间
    now = datetime.now()
    minus = now - datetime(2016, 1, 1)
    return now - timedelta(days=random.randint(0, minus.days), seconds=random.randint(1, 60),
                           minutes=random.randint(1, 60), hours=random.randint(1, 24))


def random_str(len=10):
    return codecs.encode(os.urandom(len), 'hex').decode()[:len]


def random_ch(len=2):
    common, rare = range(0x4e00, 0xa000), range(0x3400, 0x4e00)
    chars = map(unichr, rare + common)
    return u''.join([random.choice(chars) for _ in range(len)])


def bcrypt_pwd_test(pwd, validate=None):
    # 使用bcrypt生成安全的密码,且支持验证
    if not validate:
        return bcrypt.hashpw(pwd, bcrypt.gensalt())
    else:
        hashed_password = bcrypt.hashpw(pwd, validate)
        return hashed_password == validate
