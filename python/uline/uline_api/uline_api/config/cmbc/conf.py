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

sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@192.168.20.100:5432/uline'
sqlalchemy_uline_trade_db = 'postgresql+psycopg2://nbuline:Sz.t7@6ed!o2@192.168.20.90:5432/uline_trade'

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
WX_MCH_ID = '1404851802'
WXPAY_KEY = '161fc571f37e534c04c8436e1f1c0bbd'
APPID = 'wxb68005e5db5d29ce'
AppSecret = 'c05d27c5230aeb1816fd3f912f629b08'

# 正式微信公私钥(扫码支付／刷卡支付／公众账号支付)
WX_PUB_KEY = cur_dir + '/cmbc/cert/wx_prod_cert.pem'
WX_PRIVATE_KEY = cur_dir + '/cmbc/cert/wx_prod_key.pem'
WX_ROOT_CA = cur_dir + '/cmbc/cert/wx_rootca.pem'

# 微信正式商户号(APP支付)
WX_APP_MCH_ID = '1411308702'
WXPAY_APP_KEY = '937b65c2486c39d6623be64e088d1a43'
WX_APP_APPID = 'wx07241534e907ca9d'
APP_AppSecret = 'c05d27c5230aeb1816fd3f912f629b08'

# 正式微信公私钥(APP支付)
WX_APP_PUB_KEY = cur_dir + '/cmbc/cert/wx_app_prod_cert.pem'
WX_APP_PRIVATE_KEY = cur_dir + '/cmbc/cert/wx_app_prod_key.pem'
WX_APP_ROOT_CA = cur_dir + '/cmbc/cert/wx_rootca.pem'

# 微信0费率商户号(扫码支付／刷卡支付／公众账号支付)
WX_0_WX_MCH_ID = '1411308902'
WX_0_WXPAY_KEY = '3e01deea338d52f7c7bca61b52ce71ac'
WX_0_APPID = 'wxb68005e5db5d29ce'

# 正式微信公私钥(0费率)
WX_0_PUB_KEY = cur_dir + '/cmbc/cert/wx_0_rate_cert.pem'
WX_0_PRIVATE_KEY = cur_dir + '/cmbc/cert/wx_0_rate_key.pem'
WX_0_ROOT_CA = cur_dir + '/cmbc/cert/wx_rootca.pem'

# 正式支付宝商户号
ALI_APPID = '2016093002016539'
ALI_PID = '2088421939631662'

# 正式支付宝公私钥
ALI_PUB_KEY = cur_dir + '/cmbc/cert/alipay_prod_pub.key'
ALI_PRIVATE_KEY = cur_dir + '/cmbc/cert/alipay_prod_pri.key'
ALI_SERVER_ADDRESS = "https://openapi.alipay.com/gateway.do"

# 正式渠道商后台
DIST_LOGIN_URL = 'http://cms.cmbxm.mbcloud.com/dist/login'
# 正式商户后台
MCH_LOGIN_URL = 'http://cms.cmbxm.mbcloud.com/merchant/login'
# 连锁商户后台
CHAIN_LOGIN_URL = 'http://cms.cmbxm.mbcloud.com/chain/login'

# 二维码扫描地址
QR_SCAN_URL = 'http://wxpay.api.cmbxm.mbcloud.com'

# 银行名称
BANK_NAME = u'招商银行'

# 微信退款地址
WEIXIN_REFUND_URL = 'http://api.cmbxm.mbcloud.com/wechat/refunds'
# 支付宝退款地址
ALIPAY_REFUND_URL = 'http://api.cmbxm.mbcloud.com/alipay/refunds'


# 功能开关
FEATURE_SWITCH = {
    'APP_PAY': True,
    'REVIEW': True,
    # D0的开关True表示开启D0
    'OPEN_D0': False,
    '0_RATE': True,
    'CHAIN_D0': False,
    'DINE_TOGETHER': True,
    'H5': False,
    'JD_PAY': False,
    'NEW_INLET': True,
}

# ULINE API
ULINE_API_URL = 'http://ulineapi.cms.cmbxm.mbcloud.com'

# 推送交易信息银行公众号
app_id = 'wxb68005e5db5d29ce'
app_secret = 'c05d27c5230aeb1816fd3f912f629b08'
auth_access_token = u'cmbctoken'

use_secure_cookie = False


# 微信围餐费率商户号(扫码支付／刷卡支付／公众账号支付)
WX_DINE_WX_MCH_ID = '1483783812'
WX_DINE_WXPAY_KEY = 'UerA1OiAOJRotb9ltQMyjAhCVOQjad4o'
WX_DINE_APPID = 'wxb68005e5db5d29ce'

WX_DINE_PUB_KEY = cur_dir + '/cmbc/cert/wx_dine_cert.pem'
WX_DINE_PRIVATE_KEY = cur_dir + '/cmbc/cert/wx_dine_key.pem'
WX_DINE_ROOT_CA = cur_dir + '/cmbc/cert/wx_rootca.pem'
DINE_CHANNEL_ID = '35192180'

MIN_ALI_LEVEL = 'M1'
