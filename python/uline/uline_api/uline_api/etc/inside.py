#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy


SERVER_ADDRESS = '0.0.0.0'
SERVER_PORT = 9901

# DB
sqlalchemy_uline_db = 'postgresql+psycopg2://uline:uline2015@10.17.1.56/uline'
sqlalchemy_uline_trade_db = 'postgresql+psycopg2://uline:uline2015@10.17.1.56/uline_trade'


# REDIS
REDIS_DB = '13'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# 功能开关
FEATURE_SWITCH = {
    # D0的开关True表示开启D0
    'OPEN_D0': True,
    'DINE_TOGETHER': False,
    'JD_PAY': True,
    'NEW_INLET': True,
}
