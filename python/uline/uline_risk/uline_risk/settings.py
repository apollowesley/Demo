# -*- coding:utf-8 -*-

from os import (
    environ,
    path,
)

from sqlalchemy.engine.url import make_url

#
ROOT_DIR = path.dirname(path.abspath(__file__))
CONFIG_DIR = path.join(ROOT_DIR, 'config')

#
MESSAGE_URL = 'http://127.0.0.1:6789'

#
AUTH_URL = 'http://127.0.0.1:9909'

# sentry
SENTRY_DSN = 'https://1c3ebcad2af04479abc556802369c4a3:dc328f241aa54b8ca5c63a8b3bfe86be@sentry.uline.cc/4'

# env
ENV = environ.get('ENV', 'DEV')

# debug
if ENV in ('DEV', 'LOCAL'):
    DEBUG = True
else:
    DEBUG = False

# database
sqlalchemy_uline_db = environ.get(
    'ULINE_DB_DSN',
    'postgresql+psycopg2://uline:uline2015@127.0.0.1:5432/uline',
)
sqlalchemy_uline_trade_db = environ.get(
    'ULINE_TRADE_DB_DSN',
    'postgresql+psycopg2://uline:uline2015@127.0.0.1:5432/uline_trade',
)
uline_db = make_url(sqlalchemy_uline_db)
uline_trade_db = make_url(sqlalchemy_uline_trade_db)
pg_db, pg_host, pg_passwd, pg_port, pg_user = map(lambda x: getattr(uline_db, x),
                                                  ['database', 'host', 'password', 'port', 'username'])
pg_trade_db, pg_trade_host, pg_trade_passwd, pg_trade_port, pg_trade_user = map(lambda x: getattr(uline_trade_db, x),
                                                                                ['database', 'host', 'password', 'port',
                                                                                 'username'])

# server
SERVER = '127.0.0.1'
SERVER_PORT = 8835


# 支付宝测试商户号
ALI_APPID = environ.get('ALI_APPID', '2016073100137176')
ALI_PID = environ.get('ALI_PID', '2088102169373866')


# 支付宝测试公私钥
ALI_PUB_KEY = path.join(
    CONFIG_DIR,
    environ.get('ALI_PUB_KEY', 'dev/cert/alipay_dev_pub.key')
)

ALI_PRIVATE_KEY = path.join(
    CONFIG_DIR,
    environ.get('ALI_PRIVATE_KEY', 'dev/cert/alipay_dev_pri.key')
)

ALI_SERVER_ADDRESS = environ.get('ALI_SERVER_ADDRESS', 'https://openapi.alipaydev.com/gateway.do')
ALI_RISK_SERVER_ADDRESS = environ.get('ALI_RISK_SERVER_ADDRESS', 'http://openapi.stable.dl.alipaydev.com/gateway.do')
ALI_RISK_APPID = environ.get('ALI_RISK_APPID', '2017071201325188')
ALI_RISK_PID = environ.get('ALI_RISK_PID', 'xxxxxxxxxxxxxxxx')

ALI_RISK_PUB_KEY = path.join(
    CONFIG_DIR,
    environ.get('ALI_RISK_PUB_KEY', 'local/cert/alipay_mapi_pub.key')
)

ALI_RISK_PRIVATE_KEY = path.join(
    CONFIG_DIR,
    environ.get('ALI_RISK_PRIVATE_KEY', 'local/cert/alipay_mapi_pri.key')
)

RISK_SIGN_TYPE = environ.get('RISK_SIGN_TYPE', 'RSA2')
