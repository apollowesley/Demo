#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 9901


# DB
sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@192.168.20.100/uline'
sqlalchemy_uline_trade_db = 'postgresql+psycopg2://nbuline:Sz.t7@6ed!o2@192.168.20.90/uline_trade'


# REDIS
REDIS_DB = '13'
REDIS_HOST = '192.168.20.110'
REDIS_PORT = 6379

# 功能开关
FEATURE_SWITCH = {
    # D0的开关True表示开启D0
    'OPEN_D0': True,
    'DINE_TOGETHER': True,
    'JD_PAY': False,
    'NEW_INLET': True,
}
