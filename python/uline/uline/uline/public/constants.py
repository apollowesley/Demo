# -*- coding:utf-8 -*-
from uline.settings import env, FEATURE_SWITCH

BALANCE_TYPE = {'1': '企业', '2': '个人'}
BALANCE_WAY = {'0': '未定义', '1': 'T+1', '2': 'D+0'}

PAYMENT = {
    '1': '微信－扫码支付',
    '2': '微信－刷卡支付',
    '3': '微信－公众账号支付',
    '4': '微信－APP支付',
    '5': '微信－H5支付', '6': '微信某某支付',
    '7': '支付宝－扫码支付',
    '8': '支付宝－刷卡支付',
    '9': '支付宝－JS支付',
    '21': '京东－扫码支付',
    '22': '京东－刷卡支付',
    '23': '京东－公众账号支付',
    '24': '京东－H5支付',
    '25': '京东－H5支付(借记卡)',
    '33': '银联－JS支付',
}

OFFLINE_D1_WX_PAY_TYPES = [1, 2, 3]
ONLINE_D1_WX_PAY_TYPES = [4]
ONLINE_D1_WX_H5_TYPES = [5]
OFFLINE_D1_JD_PAY_TYPES = [21, 22, 23]
D1_WX_PAY_TYPES = OFFLINE_D1_WX_PAY_TYPES + ONLINE_D1_WX_H5_TYPES + ONLINE_D1_WX_PAY_TYPES
D1_ALI_PAY_TYPES = [7, 8, 9]

D1_PAY_TYPES = D1_WX_PAY_TYPES + D1_ALI_PAY_TYPES

# 银联
UNIONPAY = [33]

# 目前支持哪些支付类型
PAY_TYPES = OFFLINE_D1_WX_PAY_TYPES + ONLINE_D1_WX_PAY_TYPES + \
    ONLINE_D1_WX_H5_TYPES + D1_ALI_PAY_TYPES + OFFLINE_D1_JD_PAY_TYPES + UNIONPAY

# 连锁商户支持哪些支付类型
CHAIN_PAY_TYPES = OFFLINE_D1_WX_PAY_TYPES + \
    ONLINE_D1_WX_PAY_TYPES + D1_ALI_PAY_TYPES

ALL_WX_PAY_TYPES = OFFLINE_D1_WX_PAY_TYPES + ONLINE_D1_WX_H5_TYPES + ONLINE_D1_WX_PAY_TYPES

# 微信所有支付类型
WX_PAY_TYPES = [1, 2, 3, 4, 5, 101, 102, 103, 104, 105, 11, 12, 13]

# 支付宝所有支付类型
ALI_PAY_TYPES = [7, 8, 9, 107, 108, 109]

WX_OFFLINE_PAYTYPES = OFFLINE_D1_WX_PAY_TYPES
WX_ONLINE_PAYTYPES = ONLINE_D1_WX_PAY_TYPES + ONLINE_D1_WX_H5_TYPES
ALI_PAYTYPES = [] + (D1_ALI_PAY_TYPES)

D0_PAYMENT = {
    '101': 'D0-微信－扫码支付',
    '102': 'D0-微信－刷卡支付',
    '103': 'D0-微信－公众账号支付',
    '104': 'D0-微信－APP支付',
    '105': 'D0-微信－H5支付',
    '107': 'D0-支付宝－扫码支付',
    '108': 'D0-支付宝－刷卡支付',
    '109': 'D0-支付宝－JS支付',
}

OFFLINE_D0_WX_PAY_TYPES = [101, 102, 103]
ONLINE_D0_WX_PAY_TYPES = [104, 105]
D0_ALI_PAY_TYPES = [107, 108, 109]
D0_PAY_TYPES = OFFLINE_D0_WX_PAY_TYPES + \
    ONLINE_D0_WX_PAY_TYPES + D0_ALI_PAY_TYPES
# D0开关
if FEATURE_SWITCH.get("OPEN_D0"):
    PAYMENT.update(D0_PAYMENT)
    PAY_TYPES.extend(D0_PAY_TYPES)

    WX_OFFLINE_PAYTYPES.extend(OFFLINE_D0_WX_PAY_TYPES)
    WX_ONLINE_PAYTYPES.extend(ONLINE_D0_WX_PAY_TYPES)
    ALI_PAYTYPES.extend(D0_ALI_PAY_TYPES)

    ALL_WX_PAY_TYPES.extend(OFFLINE_D0_WX_PAY_TYPES + ONLINE_D0_WX_PAY_TYPES)

# 微信围餐
DINNER_TOGGETHER_PAYMENTS = {
    '11': '围餐-微信－扫码支付',
    '12': '围餐-微信－刷卡支付',
    '13': '围餐-微信－公众账号支付',
}
DINNER_TOGGETHER_PAY_TYPES = [11, 12, 13]
if FEATURE_SWITCH.get('DINE_TOGETHER'):
    PAYMENT.update(DINNER_TOGGETHER_PAYMENTS)
    PAY_TYPES.extend(DINNER_TOGGETHER_PAY_TYPES)
    ALL_WX_PAY_TYPES.extend(DINNER_TOGGETHER_PAY_TYPES)

ACTIVATED_STATUS = {'1': '未激活', '2': '已激活', '3': '修改中'}
# 因网络问题导致的进件失败
AUTH_STATUS = {'1': '初审中', '2': '审核通过', '3': '复审驳回', '4': '复审中', '5': '进件中', '6': '进件失败', '7': '初审驳回'}
AUTH_STATUS_SUBMIT = 1
AUTH_STATUS_ACCEPT = 2
AUTH_STATUS_DENY = 3
AUTH_STATUS_PREVIEWD = 4
AUTH_STATUS_INLETING = 5
AUTH_STATUS_INTERNET_FAIL = 6
AUTH_STATUS_FIRST_DENY = 7

WX_TRADE_TYPE = {
    'JSAPI': '公众号支付',
    'NATIVE': '扫码支付',
    'APP': 'APP 支付',
    'MWEB': 'H5 支付',
    'MICROPAY': '刷卡支付',
    'H5': 'H5 支付',
    'H5_DEBIT': 'H5 支付(借记卡)',
}
WX_TRADE_STATE = {
    'SUCCESS': '支付成功',
    'REFUND': '转入退款',
    'NOTPAY': '未支付 ',
    'CLOSED': '已关闭',
    'REVOKED': '已撤销(刷卡支付)',
    'USERPAYING': '用户支付中',
    'PAYERROR': '支付失败',
    'None': '无状态',
    'TRADE_SUCCESS': '支付成功'
}
WX_REFUND_TYPE = {'ORIGINAL': '原路退款', 'BALANCE': '退回到余额'}
WX_REFUND_STATE = {
    'SUCCESS': '退款成功',
    'FAIL': '退款失败',
    'PROCESSING': '退款处理中',
    'CHANGE': '转入代发'
}
TO_PAY = {'1': '等待划付', '2': '划付成功', '3': '划付失败', '4': '正在划付', '5': '正在划付'}

RECON_EXCEPT_TYPE = {'1': '数据错误', '2': '短帐', '3': '多帐'}
RECON_HANDLE_STATUS = {'1': '等待处理', '2': '已调账'}

PAY_CHANNEL = {'weixin': '微信', 'alipay': '支付宝', 'jdpay': '京东'}

DOWNLOAD_TYPE = {
    '1': '商户进件',
    '2': '渠道进件',
    '3': '交易对账异常',
    '4': '退款对账异常',
    '5': '商户结算',
    '6': '渠道结算',
    '7': '商户交易',
    '8': '商户退款',
    '9': '交易数据统计',
    '12': '商户对账单',
    '10': '渠道商交易数据统计',
    '11': '商户交易数据统计',
    '13': '商户转入转出',
}

DOWNLOAD_STATUS = {
    '1': '生成中',
    '2': '待下载',
    '3': '生成失败',
    '4': '已下载',
    '5': '已删除'
}

WX_USE_PARENT = {
    '1': '否',
    '2': '是'
}

# 模板文件的名字
EXCEL_TEMPLATE_PATH = 'static/handbook/ULINE_MERCHANT_INLET_TEMPLATE_V3.1.xlsx'
# 新的进件模板
MCH_EXCEL = [
    'mch_name', 'wx_pay', 'ali_pay',
    'use_dine', 'mch_front_img', 'mch_inner_img', 'mch_desk_img',
    'wx_dine_annex_img1', 'wx_dine_annex_img2', 'wx_dine_annex_img3', 'wx_dine_annex_img4', 'wx_dine_annex_img5',
    'd0_wx_pay', 'wx', 'payment_type1', 'payment_type2', 'payment_type3',
    'payment_type4', 'd0_ali_pay', 'alipay', 'payment_type7',
    'payment_type8', 'payment_type9', 'mch_shortname', 'industry_name',
    'industry_code', 'province', 'city', 'district',
    'address', 'service_phone', 'contact', 'mobile',
    'email', 'balance_type', 'balance_name', 'bank_name_com',
    'bank_name', 'bank_no', 'balance_account', 'id_card_no',
    'id_card_img_f', 'id_card_img_b', 'license_num', 'license_start_date',
    'license_end_date', 'license_period', 'license_scope', 'license_img',
    'annex_img1', 'annex_img2', 'annex_img3', 'annex_img4', 'annex_img5',
    'dt_sub_id'
]

# 连锁门店批量进件模板文件的名字
CS_EXCEL_TEMPLATE_PATH = 'static/handbook/ULINE_CS_INLET_TEMPLATE_V2.1.xlsx'
# 非D0系统的连锁商户批量进件模板
CS_EXCEL = [
    'mch_name', 'mch_shortname', 'industry_name', 'industry_code',
    # 'province', 'city', 'address', 'service_phone',
    'province', 'city', 'district', 'address', 'service_phone',
    'contact', 'mobile', 'email', 'balance_type',
    'balance_name', 'bank_name_com', 'bank_name', 'bank_no',
    'balance_account', 'id_card_no', 'id_card_img_f', 'id_card_img_b',
    'license_num', 'license_start_date', 'license_end_date', 'license_period',
    'license_scope', 'license_img', 'cs_id'
]

DOWNLOAD_FILE_NUM_LIMIT = 50
# 应产品经理需求，每次的下载都要记录
#DOWNLOAD_INFO_NUM_LIMIT = 1000 if env.lower() != 'dev' else 100
DOWNLOAD_INFO_NUM_LIMIT = 0 if env.lower() != 'dev' else 0

# 邮件服务器
SMTP_SERVER = 'mail.ulaiber.com'
SMTP_SERVER_PORT = 587
EMAIL_USER = 'uline@ulaiber.com'
EMAIL_PASSWORD = 'Uuidulaiber'
FROM_ADDR = 'uline@ulaiber.com'

MCH_CLEAR_TYPES = {
    1: u'交易',
    2: u'退款',
    3: u'D0提现',
    4: u'账务调整',
    5: u'D1划款',
}

translate_payment_type = {
    # payment_type : 'uline_payment_id|uline_settle_id|trade_type|platform_mch_id|uline_payment_code'

    # d1 微信
    1: '1|1|NATIVE|1|WX_OFFLINE_NATIVE',
    2: '2|1|MICROPAY|1|WX_OFFLINE_MICROPAY',
    3: '3|1|JSAPI|1|WX_OFFLINE_JSAPI',

    4: '4|1|APP|2|WX_ONLINE_APP',
    5: '5|1|MWEB|2|WX_ONLINE_MWEB',

    # d1 支付宝
    7: '7|1|NATIVE|5|ALI_OFFLINE_NATIVE',
    8: '8|1|MICROPAY|5|ALI_OFFLINE_MICROPAY',
    9: '9|1|JSAPI|5|ALI_OFFLINE_JSAPI',

    # d1 围餐
    11: '11|1|NATIVE|4|WX_DINE_NATIVE',
    12: '12|1|MICROPAY|4|WX_DINE_MICROPAY',
    13: '13|1|JSAPI|4|WX_DINE_JSAPI',

    # d1 围餐
    14: '14|1|NATIVE|3|WX_ZERO_NATIVE',
    15: '15|1|MICROPAY|3|WX_ZERO_MICROPAY',
    16: '16|1|JSAPI|3|WX_ZERO_JSAPI',

    17: '17|1|NATIVE|2|WX_ONLINE_NATIVE',
    18: '18|1|JSAPI|2|WX_ONLINE_JSAPI',

    # d1 微信
    21: '21|1|NATIVE|7|JD_OFFLINE_NATIVE',
    22: '22|1|MICROPAY|7|JD_OFFLINE_MICROPAY',
    23: '23|1|JSAPI|7|JD_OFFLINE_JSAPI',

    24: '24|1|H5|7|JD_ONLINE_H5',
    25: '25|1|H5_DEBIT|7|JD_ONLINE_H5_DEBIT',

    # 支付宝零费率
    27: '27|1|NATIVE|6|ALI_ZERO_NATIVE',
    28: '28|1|MICROPAY|6|ALI_ZERO_MICROPAY',
    29: '29|1|JSAPI|6|ALI_ZERO_JSAPI',

    33: '33|1|JSAPI|9|UNIONPAY_OFFLINE_JSAPI',

    # d0 微信
    101: '1|2|NATIVE|1|WX_OFFLINE_NATIVE',
    102: '2|2|MICROPAY|1|WX_OFFLINE_MICROPAY',
    103: '3|2|JSAPI|1|WX_OFFLINE_JSAPI',
    104: '4|2|APP|2|WX_ONLINE_APP',
    105: '5|2|MWEB|2|WX_ONLINE_MWEB',

    # d0 支付宝
    107: '7|2|NATIVE|5|ALI_OFFLINE_NATIVE',
    108: '8|2|MICROPAY|5|ALI_OFFLINE_MICROPAY',
    109: '9|2|JSAPI|5|ALI_OFFLINE_JSAPI',

    # d1 围餐
    111: '111|2|MICROPAY|4|WX_DINE_NATIVE',
    112: '112|2|MICROPAY|4|WX_DINE_MICROPAY',
    113: '113|2|MICROPAY|4|WX_DINE_JSAPI',

    117: '17|2|NATIVE|2|WX_ONLINE_NATIVE',
    118: '18|2|JSAPI|2|WX_ONLINE_JSAPI',

}

# 有效的支付方式
AVAILABLE_PAYMENTS = {
    # 微信线下支付
    'WX_OFFLINE_NATIVE': u'微信线下扫码支付',
    'WX_OFFLINE_MICROPAY': u'微信线下刷卡支付',
    'WX_OFFLINE_JSAPI': u'微信线下公众账号支付',

    # 微信线上支付
    'WX_ONLINE_NATIVE': u'微信线上扫码支付',
    'WX_ONLINE_JSAPI': u'微信线上公众账号支付',
    'WX_ONLINE_APP': u'微信线上APP支付',
    'WX_ONLINE_MWEB': u'微信线上H5支付',

    # 微信围餐
    'WX_DINE_NATIVE': u'微信围餐扫码支付',
    'WX_DINE_MICROPAY': u'微信围餐刷卡支付',
    'WX_DINE_JSAPI': u'微信围餐公众账号支付',

    # 微信零费率
    'WX_ZERO_NATIVE': u'微信零费率扫码支付',
    'WX_ZERO_MICROPAY': u'微信零费率刷卡支付',
    'WX_ZERO_JSAPI': u'微信零费率公众账号支付',

    # 支付宝线下
    'ALI_OFFLINE_NATIVE': u'支付宝线下扫码支付',
    'ALI_OFFLINE_MICROPAY': u'支付宝线下刷卡支付',
    'ALI_OFFLINE_JSAPI': u'支付宝线下JS支付',

    # 京东线下
    'JD_OFFLINE_NATIVE': u'京东线下扫码支付',
    'JD_OFFLINE_MICROPAY': u'京东线下刷卡支付',
    'JD_OFFLINE_JSAPI': u'京东线下公众账号支付',

    # 京东线上
    'JD_ONLINE_H5': u'京东线上H5支付',
    'JD_ONLINE_H5_DEBIT': u'京东线上H5支付(借记卡)',

    # 支付宝零费率
    'ALI_ZERO_NATIVE': u'支付宝零费率扫码支付',
    'ALI_ZERO_MICROPAY': u'支付宝零费率刷卡支付',
    'ALI_ZERO_JSAPI': u'支付宝零费率JS支付',

    # d0 (临时，后期将删除)

    # 微信线下支付
    'WX_OFFLINE_NATIVE_D0': u'D0微信线下扫码支付',
    'WX_OFFLINE_MICROPAY_D0': u'D0微信线下刷卡支付',
    'WX_OFFLINE_JSAPI_D0': u'D0微信线下公众账号支付',

    # 微信线上支付
    'WX_ONLINE_NATIVE_D0': u'D0微信线上扫码支付',
    'WX_ONLINE_JSAPI_D0': u'D0微信线上公众账号支付',
    'WX_ONLINE_APP_D0': u'D0微信线上APP支付',
    'WX_ONLINE_MWEB_D0': u'D0微信线上H5支付',

    # 微信围餐
    'WX_DINE_NATIVE_D0': u'D0微信围餐扫码支付',
    'WX_DINE_MICROPAY_D0': u'D0微信围餐刷卡支付',
    'WX_DINE_JSAPI_D0': u'D0微信围餐公众账号支付',

    # 微信零费率
    # 'WX_ZERO_NATIVE_D0': u'D0微信零费率扫码支付',
    # 'WX_ZERO_MICROPAY_D0': u'D0微信零费率刷卡支付',
    # 'WX_ZERO_JSAP_D0': u'D0微信零费率公众账号支付',

    # 支付宝线下
    'ALI_OFFLINE_NATIVE_D0': u'D0支付宝线下扫码支付',
    'ALI_OFFLINE_MICROPAY_D0': u'D0支付宝线下刷卡支付',
    'ALI_OFFLINE_JSAPI_D0': u'D0支付宝线下JS支付',

    # 银联
    'UNIONPAY_OFFLINE_JSAPI': u'D1银联线下JS支付',
    # '1': u'微信－扫码支付',
    # '2': u'微信－刷卡支付',
    # '3': u'微信－公众账号支付',
    # '4': u'微信－APP支付',
    # '5': u'微信－H5支付',
    # '6': u'微信某某支付',
    # '7': u'支付宝－扫码支付',
    # '8': u'支付宝－刷卡支付',
    # '9': u'支付宝－JS支付'
}

AVAILABLE_PAYMENTS_FORMAT = {
    # 微信线下支付
    'WX_OFFLINE_NATIVE': '微信-扫码支付（线下D1）',
    'WX_OFFLINE_MICROPAY': '微信-刷卡支付（线下D1）',
    'WX_OFFLINE_JSAPI': '微信-公众账号支付（线下D1）',

    # 微信线上支付
    'WX_ONLINE_NATIVE': '微信-扫码支付（线上D1）',
    'WX_ONLINE_JSAPI': '微信-公众账号支付（线上D1）',
    'WX_ONLINE_APP': '微信-APP支付（线上D1）',
    'WX_ONLINE_MWEB': '微信-H5支付（线上D1）',

    # 微信围餐
    'WX_DINE_NATIVE': '微信-扫码支付（围餐）',
    'WX_DINE_MICROPAY': '微信-刷卡支付（围餐）',
    'WX_DINE_JSAPI': '微信-公众账号支付（围餐）',

    # 微信零费率
    'WX_ZERO_NATIVE': '微信-扫码支付（零费率）',
    'WX_ZERO_MICROPAY': '微信-刷卡支付（零费率）',
    'WX_ZERO_JSAPI': '微信-公众账号支付（零费率）',

    # 支付宝线下
    'ALI_OFFLINE_NATIVE': '支付宝-扫码支付（线下D1）',
    'ALI_OFFLINE_MICROPAY': '支付宝-刷卡支付（线下D1）',
    'ALI_OFFLINE_JSAPI': '支付宝-JS支付（线下D1）',

    # 支付宝线下
    'JD_OFFLINE_NATIVE': '京东-扫码支付（线下T1）',
    'JD_OFFLINE_MICROPAY': '京东-刷卡支付（线下T1）',
    'JD_OFFLINE_JSAPI': '京东-公众账号支付（线下T1）',

    # 京东线上
    'JD_ONLINE_H5': '京东-H5支付（线下T1）',
    'JD_ONLINE_H5_DEBIT': '京东-H5支付（借记卡)(线下T1）',

    # d0 (临时，后期将删除)
    # 微信线下支付
    'WX_OFFLINE_NATIVE_D0': '微信-扫码支付（线下D0）',
    'WX_OFFLINE_MICROPAY_D0': '微信-刷卡支付（线下D0）',
    'WX_OFFLINE_JSAPI_D0': '微信-公众账号支付（线下D0）',

    # 微信线上支付
    'WX_ONLINE_NATIVE_D0': '微信-扫码支付（线上D0）',
    'WX_ONLINE_JSAPI_D0': '微信-公众账号支付（线上D0）',
    'WX_ONLINE_APP_D0': '微信-APP支付（线上D0）',
    'WX_ONLINE_MWEB_D0': '微信-H5支付（线上D0）',

    # 支付宝线下
    'ALI_OFFLINE_NATIVE_D0': '支付宝-扫码支付（线下D0）',
    'ALI_OFFLINE_MICROPAY_D0': '支付宝-刷卡支付（线下D0）',
    'ALI_OFFLINE_JSAPI_D0': '支付宝-JS支付（线下D0）',

    'UNIONPAY_OFFLINE_JSAPI': '银联-JS支付(线下D1)'
}


old_payment_relations = {
    # d1
    # 微信线下
    '1': 'WX_OFFLINE_NATIVE',
    '2': 'WX_OFFLINE_MICROPAY',
    '3': 'WX_OFFLINE_JSAPI',


    # 微信线上支付
    '17': 'WX_ONLINE_NATIVE',
    '18': 'WX_ONLINE_JSAPI',
    '4': 'WX_ONLINE_APP',
    '5': 'WX_ONLINE_MWEB',

    # 支付宝线下
    '7': 'ALI_OFFLINE_NATIVE',
    '8': 'ALI_OFFLINE_MICROPAY',
    '9': 'ALI_OFFLINE_JSAPI',

    # 微信围餐
    '11': 'WX_DINE_NATIVE',
    '12': 'WX_DINE_MICROPAY',
    '13': 'WX_DINE_JSAPI',

    # 微信0费率
    '14': 'WX_ZERO_NATIVE',
    '15': 'WX_ZERO_MICROPAY',
    '16': 'WX_ZERO_JSAPI',

    # 京东线下
    '21': 'JD_OFFLINE_NATIVE',
    '22': 'JD_OFFLINE_MICROPAY',
    '23': 'JD_OFFLINE_JSAPI',

    # 京东线上
    '24': 'JD_ONLINE_H5',
    '25': 'JD_ONLINE_H5_DEBIT',

    # 支付宝零费率
    '27': 'ALI_ZERO_NATIVE',
    '28': 'ALI_ZERO_MICROPAY',
    '29': 'ALI_ZERO_JSAPI',

    # 银联支付
    '33': 'UNIONPAY_OFFLINE_JSAPI',

    # d0
    # 微信线下
    '101': 'WX_OFFLINE_NATIVE_D0',
    '102': 'WX_OFFLINE_MICROPAY_D0',
    '103': 'WX_OFFLINE_JSAPI_D0',


    # 微信线上支付
    '117': 'WX_ONLINE_NATIVE_D0',
    '118': 'WX_ONLINE_JSAPI_D0',
    '104': 'WX_ONLINE_APP_D0',
    '105': 'WX_ONLINE_MWEB_D0',

    # 支付宝线下
    '107': 'ALI_OFFLINE_NATIVE_D0',
    '108': 'ALI_OFFLINE_MICROPAY_D0',
    '109': 'ALI_OFFLINE_JSAPI_D0',

    # 微信围餐
    '111': 'WX_DINE_NATIVE_D0',
    '112': 'WX_DINE_MICROPAY_D0',
    '113': 'WX_DINE_JSAPI_D0',

    # # 微信0费率
    # '114': 'WX_ZERO_NATIVE_D0',
    # '115': 'WX_ZERO_MICROPAY_D0',
    # '116': 'WX_ZERO_JSAPI_D0',
}

new_payment_relations = dict([(v, int(k)) for k, v in old_payment_relations.iteritems()])

# 排序
rate_sort = {
    'WX_OFFLINE_NATIVE': 1,
    'WX_OFFLINE_MICROPAY': 2,
    'WX_OFFLINE_JSAPI': 3,

    'WX_ONLINE_NATIVE': 4,
    'WX_ONLINE_JSAPI': 5,
    'WX_ONLINE_APP': 6,
    'WX_ONLINE_MWEB': 7,

    'WX_DINE_NATIVE': 11,
    'WX_DINE_MICROPAY': 12,
    'WX_DINE_JSAPI': 13,

    'WX_ZERO_NATIVE': 14,
    'WX_ZERO_MICROPAY': 15,
    'WX_ZERO_JSAPI': 16,

    'JD_OFFLINE_NATIVE': 21,
    'JD_OFFLINE_MICROPAY': 22,
    'JD_OFFLINE_JSAPI': 23,
    'JD_ONLINE_H5': 24,
    'JD_ONLINE_H5_DEBIT': 25,

    'ALI_OFFLINE_NATIVE': 27,
    'ALI_OFFLINE_MICROPAY': 28,
    'ALI_OFFLINE_JSAPI': 29,

    'ALI_ZERO_NATIVE': 31,
    'ALI_ZERO_MICROPAY': 32,
    'ALI_ZERO_JSAPI': 33,

    'UNIONPAY_OFFLINE_JSAPI': 35,

    'WX_OFFLINE_NATIVE_D0': 101,
    'WX_OFFLINE_MICROPAY_D0': 102,
    'WX_OFFLINE_JSAPI_D0': 103,

    'WX_ONLINE_NATIVE_D0': 104,
    'WX_ONLINE_JSAPI_D0': 105,
    'WX_ONLINE_APP_D0': 106,
    'WX_ONLINE_MWEB_D0': 107,

    'WX_DINE_NATIVE_D0': 111,
    'WX_DINE_MICROPAY_D0': 112,
    'WX_DINE_JSAPI_D0': 113,

    'WX_ZERO_NATIVE_D0': 114,
    'WX_ZERO_MICROPAY_D0': 115,
    'WX_ZERO_JSAPI_D0': 116,

    'ALI_OFFLINE_NATIVE_D0': 117,
    'ALI_OFFLINE_MICROPAY_D0': 118,
    'ALI_OFFLINE_JSAPI_D0': 119,

    'ALI_ZERO_NATIVE_D0': 121,
    'ALI_ZERO_MICROPAY_D0': 122,
    'ALI_ZERO_JSAPI_D0': 123,

}


MCH_CLEAR_ACTIONS = {
    1: u"收款",
    2: u"退款",
    3: u"提现",
    4: u"调整",
    5: u"划款",

}

# 默认同业银行密码
DEFAULT_INTER_BANK_PASSWORD = "123456"

# 银行类型 main为主银行，inter为同业银行
BANK_TYPE = {"main": 1, "inter": 2}
CHANGE_RECORD_STATUS_SUBMIT = 1
CHANGE_RECORD_STATUS_ACCEPT = 2
CHANGE_RECORD_STATUS_DENY = 3
CHANGE_RECORD_STATUS_TO_CUT = 4

RISK_TYPE_MAP = {
    'cert_no': u'身份证风险',
    'bank_card_no': u'银行卡风险',
    'business_license_no': u'营业执照风险'
}

RISK_INFO_MAP = {
    'cert_no': u'身份证',
    'bank_card_no': u'银行卡',
    'business_license_no': u'营业执照'
}


LICENSE_TYPE_MAP = {
    "NATIONAL_LEGAL": "营业执照",
    "NATIONAL_LEGAL_MERGE": "营业执照（多证合一)",
    "INST_RGST_CTF": "事业单位法人证书"
}

HEAD_TYPE_MAP = {
    'LEGAL_PERSON': '法人',
    'CONTROLLER': '控制人',
    'AGENT': '代理人',
    'OTHER': '其他',
}
