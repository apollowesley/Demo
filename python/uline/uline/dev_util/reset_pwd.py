#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '3/9/17'

# 为了方便本地测试,将所有用户的密码均设置为123456($2b$12$7InEXPbtETn9N6s3JMgzjOmqBAAATnU.JLPgkwSvhWbOs6z5JW.jm)
# PYTHONPATH=. python dev_util/reset_pwd.py

from uline.public.db import initdb, uline_session_scope
from uline.model.uline.user import MchUser, DtUser, BkUser, UbUser
from uline.settings import env

if env != 'LOCAL':
    raise Exception(u'只能在本地环境下执行重置操作')

initdb()

with uline_session_scope() as session:
    for i in MchUser.get_by(session):
        i.password = '$2b$12$7InEXPbtETn9N6s3JMgzjOmqBAAATnU.JLPgkwSvhWbOs6z5JW.jm'

    for i in session.query(DtUser):
        i.password = '$2b$12$7InEXPbtETn9N6s3JMgzjOmqBAAATnU.JLPgkwSvhWbOs6z5JW.jm'

    for i in session.query(BkUser):
        i.password = '$2b$12$7InEXPbtETn9N6s3JMgzjOmqBAAATnU.JLPgkwSvhWbOs6z5JW.jm'

    for i in session.query(UbUser):
        i.password = '$2b$12$7InEXPbtETn9N6s3JMgzjOmqBAAATnU.JLPgkwSvhWbOs6z5JW.jm'

    print('mch: {}'.format(session.query(MchUser).first().mch_id))
    print('dt: {}'.format(session.query(DtUser).first().email))
    print('bank {}'.format(session.query(BkUser).first().email))
    print('official: {}'.format(session.query(UbUser).first().email))
