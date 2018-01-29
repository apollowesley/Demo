# -*- coding:utf-8 -*-
# bank test environment
from uline_api.config.base import *
from os import path

from sqlalchemy.engine.url import make_url

cur_dir = path.dirname(path.dirname(path.abspath(__file__)))

# default port
portDFLT = 8888
server_port = str(portDFLT)

# debug
server_debug = True
# redis配置
redis_db = 1
redis_host = 'localhost'
redis_port = 6379


sqlalchemy_uline_db = 'postgresql+psycopg2://uline:uline2015@127.0.0.1:5432/uline'
sqlalchemy_uline_trade_db = 'postgresql+psycopg2://uline:uline2015@127.0.0.1:5432/uline_trade'

uline_db = make_url(sqlalchemy_uline_db)
uline_trade_db = make_url(sqlalchemy_uline_trade_db)
pg_db, pg_host, pg_passwd, pg_port, pg_user = map(lambda x: getattr(uline_db, x),
                                                  ['database', 'host', 'password', 'port', 'username'])

pg_trade_db, pg_trade_host, pg_trade_passwd, pg_trade_port, pg_trade_user = map(lambda x: getattr(uline_trade_db, x),
                                                                                ['database', 'host', 'password', 'port',
                                                                                 'username'])

server = '127.0.0.1'
server_port = str(int(server_port) + 5)
BaseUrl = "http://" + server + ":" + server_port + "/"

# 微信测试商户号(扫码支付／刷卡支付／公众账号支付)
WX_MCH_ID = '1900008951'
WXPAY_KEY = '3AC991426F056322E053645AA8C0CC12'
APPID = 'wxdace645e0bc2c424'

# 微信测试0费率商户号(扫码支付／刷卡支付／公众账号支付)
WX_0_WX_MCH_ID = '1900008951'
WX_0_WXPAY_KEY = '3AC991426F056322E053645AA8C0CC12'
WX_0_APPID = 'wxdace645e0bc2c424'
AppSecret = ''

# 微信测试公私钥(扫码支付／刷卡支付／公众账号支付)
WX_PUB_KEY = cur_dir + '/dev/cert/wx_dev_cert.pem'
WX_PRIVATE_KEY = cur_dir + '/dev/cert/wx_dev_key.pem'
WX_ROOT_CA = cur_dir + '/dev/cert/wx_rootca.pem'

# 微信测试公私钥(0费率)
WX_0_PUB_KEY = cur_dir + '/dev/cert/wx_dev_cert.pem'
WX_0_PRIVATE_KEY = cur_dir + '/dev/cert/wx_dev_key.pem'
WX_0_ROOT_CA = cur_dir + '/dev/cert/wx_rootca.pem'

# 微信测试商户号(APP支付)
WX_APP_MCH_ID = '1900008951'
WXPAY_APP_KEY = '3AC991426F056322E053645AA8C0CC12'
WX_APP_APPID = 'wxdace645e0bc2c424'
APP_AppSecret = ''

# 微信测试公私钥(APP支付)
WX_APP_PUB_KEY = cur_dir + '/dev/cert/wx_dev_cert.pem'
WX_APP_PRIVATE_KEY = cur_dir + '/dev/cert/wx_dev_key.pem'
WX_APP_ROOT_CA = cur_dir + '/dev/cert/wx_rootca.pem'

# 支付宝测试商户号
ALI_APPID = '2016073100137176'
ALI_PID = '2088102169373866'
# 支付宝测试公私钥
ALI_PUB_KEY = cur_dir + '/dev/cert/alipay_dev_pub.key'
ALI_PRIVATE_KEY = cur_dir + '/dev/cert/alipay_dev_pri.key'
ALI_SERVER_ADDRESS = "https://openapi.alipaydev.com/gateway.do"

# 测试渠道商后台
DIST_LOGIN_URL = 'http://mch.stage.uline.cc/dist/login'
# 测试商户后台
MCH_LOGIN_URL = 'http://mch.stage.uline.cc/merchant/login'
# 测试连锁商户后台
CHAIN_LOGIN_URL = 'http://mch.stage.uline.cc/chain/login'

# 二维码扫描地址
QR_SCAN_URL = 'http://wxpay.api.cmbxm.mbcloud.com'

# 银行名称
BANK_NAME = u'DEV'

# 微信退款地址
WEIXIN_REFUND_URL = 'http://api.stage.uline.cc/wechat/refunds'
# 支付宝退款地址
ALIPAY_REFUND_URL = 'http://api.stage.uline.cc/alipay/refunds'

# 功能开关
FEATURE_SWITCH = {
    'APP_PAY': True,
    'REVIEW': False,
    # D0的开关True表示开启D0
    'OPEN_D0': True,
    '0_RATE': True,
    'CHAIN_D0': False,
    'DINE_TOGETHER': True,
    'H5': False,
    'JD_PAY': True,
    'NEW_INLET': True,
}

# ULINE API
ULINE_API_URL = 'http://pay.stage.uline.cc'


# 推送交易信息银行公众号
app_id = 'wx31d61acccc4db8c0'
app_secret = '3e5efe5bd8b748ae301ffb5424207c78'
auth_access_token = u'dfcdrgdyhegtr4w5cw555w45'


use_secure_cookie = False


# 微信围餐费率商户号(扫码支付／刷卡支付／公众账号支付)
WX_DINE_WX_MCH_ID = '1900008951'
WX_DINE_WXPAY_KEY = '3AC991426F056322E053645AA8C0CC12'
WX_DINE_APPID = 'wxdace645e0bc2c424'

WX_DINE_PUB_KEY = cur_dir + '/dev/cert/wx_dev_cert.pem'
WX_DINE_PRIVATE_KEY = cur_dir + '/dev/cert/wx_dev_key.pem'
WX_DINE_ROOT_CA = cur_dir + '/dev/cert/wx_rootca.pem'
DINE_CHANNEL_ID = '26460047'

MIN_ALI_LEVEL = 'M3'
