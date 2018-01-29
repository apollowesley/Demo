# -*- coding:utf-8 -*-
# bank prod environment
from uline_api.config.base import *
from os import path

from sqlalchemy.engine.url import make_url

cur_dir = path.dirname(path.dirname(path.abspath(__file__)))


# default port
portDFLT = 8888
server_port = str(portDFLT)

server_debug = False

sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@192.168.20.100:5432/spd_uline'
sqlalchemy_uline_trade_db = 'postgresql+psycopg2://nbuline:Sz.t7@6ed!o2@192.168.20.90:5432/spd_uline_trade'

uline_db = make_url(sqlalchemy_uline_db)
uline_trade_db = make_url(sqlalchemy_uline_trade_db)
pg_db, pg_host, pg_passwd, pg_port, pg_user = map(lambda x: getattr(uline_db, x),
                                                  ['database', 'host', 'password', 'port', 'username'])

pg_trade_db, pg_trade_host, pg_trade_passwd, pg_trade_port, pg_trade_user = map(lambda x: getattr(uline_trade_db, x),
                                                                                ['database', 'host', 'password', 'port',
                                                                                 'username'])

redis_db = 1
redis_host = '192.168.20.110'
redis_port = 6379

server = '127.0.0.1'
BaseUrl = "http://" + server + ":" + server_port + "/"
server_port = str(int(server_port) + 6)

# 微信正式商户号(扫码支付／刷卡支付／公众账号支付)
WX_MCH_ID = '1399380202'
WXPAY_KEY = '365235dab287f56cf194d85a1cd17093'
APPID = 'wx6c9a41cd28bf89ea'
AppSecret = ''

# 正式微信公私钥(扫码支付／刷卡支付／公众账号支付)
WX_PUB_KEY = cur_dir + '/spd/cert/wx_prod_cert.pem'
WX_PRIVATE_KEY = cur_dir + '/spd/cert/wx_prod_key.pem'
WX_ROOT_CA = cur_dir + '/spd/cert/wx_rootca.pem'

# 微信正式商户号(APP支付)
WX_APP_MCH_ID = '1436104302'
WXPAY_APP_KEY = '9e0a545a9c171a23c10a7b99a3a7526f'
WX_APP_APPID = 'wxf0a7fb05f98bc6fb'
APP_AppSecret = ''

# 正式微信公私钥(APP支付)
WX_APP_PUB_KEY = cur_dir + '/spd/cert/wx_app_prod_cert.pem'
WX_APP_PRIVATE_KEY = cur_dir + '/spd/cert/wx_app_prod_key.pem'
WX_APP_ROOT_CA = cur_dir + '/spd/cert/wx_app_rootca.pem'

# 正式支付宝商户号
ALI_APPID = '2016112903553069'
ALI_PID = '2088221492527297'

# 正式支付宝公私钥
ALI_PUB_KEY = cur_dir + '/spd/cert/alipay_prod_pub.key'
ALI_PRIVATE_KEY = cur_dir + '/spd/cert/alipay_prod_pri.key'
ALI_SERVER_ADDRESS = "https://openapi.alipay.com/gateway.do"

# 微信测试0费率商户号(扫码支付／刷卡支付／公众账号支付)
WX_0_WX_MCH_ID = '1900008951'
WX_0_WXPAY_KEY = '3AC991426F056322E053645AA8C0CC12'
WX_0_APPID = 'wxdace645e0bc2c424'

# 微信测试公私钥(0费率) 浦发没有提供
WX_0_PUB_KEY = cur_dir + '/dev/cert/wx_dev_cert.pem'
WX_0_PRIVATE_KEY = cur_dir + '/dev/cert/wx_dev_key.pem'
WX_0_ROOT_CA = cur_dir + '/dev/cert/wx_rootca.pem'

# 正式渠道商后台
DIST_LOGIN_URL = 'http://cms.spd.uline.cc/dist/login'
# 正式商户后台
MCH_LOGIN_URL = 'http://cms.spd.uline.cc/merchant/login'
# 连锁商户后台
CHAIN_LOGIN_URL = 'http://cms.spd.uline.cc/chain/login'

# 二维码扫描地址
QR_SCAN_URL = 'http://pay.spd.uline.cc'

# 银行名称
BANK_NAME = u'浦发银行'

# 微信退款地址
WEIXIN_REFUND_URL = 'http://api.mch.spd.uline.cc/wechat/refunds'
# 支付宝退款地址
ALIPAY_REFUND_URL = 'http://api.mch.spd.uline.cc/alipay/refunds'

# 功能开关
FEATURE_SWITCH = {
    'APP_PAY': True,
    'REVIEW': False,
    # D0的开关True表示开启D0
    'OPEN_D0': True,
    '0_RATE': False,
    'CHAIN_D0': False,
    'DINE_TOGETHER': False,
    'H5': True,
    'JD_PAY': True,
    'NEW_INLET': True,
}

# ULINE API
ULINE_API_URL = 'https://dtapi.spd.uline.cc'

# 推送交易信息银行公众号
app_id = 'wxf0a7fb05f98bc6fb'
app_secret = '939eec2c5cce2dae9c75829748d3cdeb'
auth_access_token = u'spdtoken'

use_secure_cookie = False


# 微信围餐费率商户号(扫码支付／刷卡支付／公众账号支付)
WX_DINE_WX_MCH_ID = '1900008951'
WX_DINE_WXPAY_KEY = '3AC991426F056322E053645AA8C0CC12'
WX_DINE_APPID = 'wxdace645e0bc2c424'

WX_DINE_PUB_KEY = cur_dir + '/dev/cert/wx_dev_cert.pem'
WX_DINE_PRIVATE_KEY = cur_dir + '/dev/cert/wx_dev_key.pem'
WX_DINE_ROOT_CA = cur_dir + '/dev/cert/wx_rootca.pem'
DINE_CHANNEL_ID = ''

MIN_ALI_LEVEL = 'M3'
