# -*- coding: utf-8 -*-
import json
import urllib
from datetime import datetime
import logging
import os
import traceback

from tornado.httpclient import HTTPClient

from uline.public.common import gen_randown_mch_pkey
from uline.public.constants import AUTH_STATUS, ACTIVATED_STATUS
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA, ALI_APPID, ALI_PID,
)

from uline.utils.wxpay.merchantInletToWxV2 import MerchantInletToWx, UpdateMerchantInletToWx
from uline.settings import env, MCH_LOGIN_URL, MESSAGE_URL


from uline.backend.__init__ import *


from uline.public import common, log
from uline.utils.alipay.merchantInletToAlipay import AliRSAEncryptionClass
from uline.utils.wxpay.util import xml_to_dict

from uline.backend import tasks

logger = logging.getLogger('my_auto_review')
file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
filelog = logging.FileHandler(file_path + '/log/auto_review.log')
filelog.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filelog.setFormatter(formatter)
logger.addHandler(filelog)
logger.info('auto_review')


def automatic_review(mch_ids):
    failed_ids = []
    failed_inlet_3party = []
    for mch_id in mch_ids:
        wx_flag = wx_app_flag = ali_flag = True
        update_at = common.timestamp_now()

        mch_status = 1
        has_active_payments = False
        with db.get_db() as cur:
            try:
                mch_inlet_info = get_mch_inlet_info(mch_id, cur)
                record = get_mch_change_record(cur, mch_id)
                # 进件逻辑
                # 如果状态是审核中，则继续走审核流程，否则，完全跳过
                if mch_inlet_info[10] == 1 and not record:
                    mch_wx_payment = get_mch_payment(mch_id, cursor=cur, pay_type='weixin')
                    mch_wx_app_payment = get_mch_payment(mch_id, cursor=cur, pay_type='weixin', wx_app=True)
                    mch_ali_payment = get_mch_payment(mch_id, cursor=cur, pay_type='alipay')

                    wx_ali_id = get_mch_user_wx_ali_id(mch_id, cur)

                    alipay_category_id = get_mch_alipay_category_id(mch_id, cur)

                    wx_flag, msg_wx = mch_inlet_to_wx_reg(mch_id,
                                                          cur, wx_flag, mch_wx_payment, wx_ali_id, mch_inlet_info,
                                                          update_at)
                    wx_app_flag, msg_app_wx = mch_inlet_to_wx_app(mch_id,
                                                                  cur, wx_app_flag, mch_wx_app_payment,
                                                                  wx_ali_id, mch_inlet_info, update_at)
                    ali_flag, msg_ali = mch_inlet_to_ali_reg(mch_id,
                                                             cur, ali_flag, mch_ali_payment,
                                                             wx_ali_id, mch_inlet_info, alipay_category_id, update_at)

                    if not (wx_flag and wx_app_flag and ali_flag):
                        comment_news = [msg_wx, msg_app_wx, msg_ali]
                        field = ["微信支付进件:{}", "微信APP进件:{}", "支付宝进件:{}"]
                        show_comment = " ".join(
                            _f.format(_com) for _f, _com in zip(field, comment_news) if _com != "success")
                        add_fail_auth_inlet_info(mch_id, cur, show_comment, update_at)
                        auth_status = 3
                        auth_mch_inlet(mch_id, cur, auth_status, update_at)
                        mch_status = 1
                        failed_inlet_3party.append(mch_id)
                        logger.info("进件到微信、支付宝失败：{},{}".format(mch_id, show_comment))
                    else:
                        mch_status = 2
                        auth_status = 2
                        update_mch_user(mch_id, cur, mch_status, update_at)
                        auth_mch_inlet(mch_id, cur, auth_status, update_at)

                        # 修改微信端商户信息(包括商户简称和服务电话)
                        # update_wx_mch(mch_id, wx_ali_id[2], cur, update_at)

                        add_auth_inlet_info(mch_id, cur, auth_status, update_at)

                else:
                    continue

                if mch_status == 2:
                    # 如果审核通过，则激活支付方式
                    has_active_payments = automatic_activate(cur, mch_id, update_at)
            except Exception as err:
                cur.connection.rollback()
                failed_ids.append(mch_id)
                logger.exception(traceback.format_exc())
                logger.exception('商户号{}进件失败'.format(mch_id))
                has_active_payments = False
                mch_status = 1
                raise
            else:
                try:
                    cur.connection.commit()
                except Exception as err:
                    log.exception.info(err)
                    cur.connection.rollback()
                    logger.exception(traceback.format_exc())
                    logger.exception('商户号{}进件失败 in commit'.format(mch_id))
                    has_active_payments = False
                    mch_status = 1
                    raise

            # 数据库操作完成后，通知商户
        message_id = gen_randown_mch_pkey(8)
        tasks.callback_for_merchant_status.apply_async((mch_id, mch_status, message_id),)

        if has_active_payments:
            # 激活支付方式后通知商户
            with db.get_db() as cur:
                notify_mch(cur, mch_id, update_at)

        if mch_status == 2:
            logger.info("进件成功，{}".format(mch_id))

    if failed_inlet_3party:
        logger.info("进件到微信或支付宝失败的商户:{}".format(failed_inlet_3party))


def get_mch_payment(mch_id, cursor=None, pay_type=None, wx_app=False):
    if pay_type == 'weixin':
        query = """select id from mch_payment
        where mch_id=%s and payment_type in (1,2,3);"""
        if wx_app:
            query = """select id from mch_payment
                        where mch_id=%s and payment_type=4;"""
    elif pay_type == 'alipay':
        query = """select id from mch_payment
        where mch_id=%s and payment_type in (7,8,9);"""
    else:
        query = """"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def get_mch_user_wx_ali_id(mch_id, cursor):
    query = """select
            mch_user.wx_sub_mch_id,
            mch_user.ali_sub_mch_id,
            mch_user.wx_use_parent,
            mch_user.wx_app_sub_mch_id
            from mch_user
            where mch_user.mch_id=%s"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def get_mch_inlet_info(mch_id, cursor):
    query = """select
            mch_name,
            mch_shortname,
            service_phone,
            contact,
            mobile,
            email,
            old_ind_code,
            wx_ind_code,
            u_ind_code,
            ali_ind_code,
            auth_status,
            activated_status
            from
            mch_inlet_info
            where mch_id=%s;"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def get_mch_alipay_category_id(mch_id, cursor):
    query = """select ali_ind_code from mch_inlet_info where mch_id=%s;"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret[0]


def mch_inlet_to_wx_reg(mch_id, cur, wx_flag, mch_wx_payment, wx_ali_id, mch_inlet_info, update_at):
    # 微信支付(扫码支付／刷卡支付／公众账号支付)
    msg_wx = "success"
    if mch_wx_payment and (
            wx_ali_id[2] == 1):
        ret = create_wx_sub_mch_id(mch_id,
                                   mch_inlet_info, APPID, WX_MCH_ID, WXPAY_KEY,
                                   WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        log.exception.info('reg:{}'.format(ret))
        save_mch_inlet_to_wx(mch_id, cur, ret, update_at)
        wx_sub_mch_id = ret.get('sub_mch_id') if ret.get(
            'return_code') == 'SUCCESS' else ''
        if not wx_sub_mch_id:
            wx_flag = False
            msg_wx = ret.get('result_msg', '进件到微信支付出现未知错误!请联系客服!')
        else:
            add_wx_sub_mch_id(mch_id, cur, wx_sub_mch_id, update_at)

    elif mch_wx_payment and (wx_ali_id[2] == 2):
        # 使用渠道商微信支付(扫码支付／刷卡支付／公众账号支付)
        ret = get_dt_wx_pay_info(mch_id, cur)
        if ret[0]:
            update_mch_wx_pay_info(mch_id, cur, ret)
        else:
            wx_flag = False
    wx_reg = [wx_flag, msg_wx]
    return wx_reg


def add_wx_sub_mch_id(mch_id, cursor, wx_sub_mch_id, update_at):
    query = """update mch_user set wx_sub_mch_id=%s,update_at=%s where mch_id=%s"""
    cursor.execute(query, (wx_sub_mch_id,
                           update_at, mch_id))


def mch_inlet_to_wx_app(mch_id, cur, wx_app_flag, mch_wx_app_payment, wx_ali_id, mch_inlet_info, update_at):
    # 微信支付(APP支付)
    msg_app_wx = "success"
    if mch_wx_app_payment and (wx_ali_id[2] == 1):
        ret = create_wx_sub_mch_id(mch_id,
                                   mch_inlet_info, WX_APP_APPID, WX_APP_MCH_ID, WXPAY_APP_KEY,
                                   WX_APP_PRIVATE_KEY, WX_APP_PUB_KEY, WX_APP_ROOT_CA)
        log.exception.info('app:{}'.format(ret))
        save_mch_inlet_to_wx(mch_id, cur, ret, update_at)
        wx_app_sub_mch_id = ret.get('sub_mch_id') if ret.get(
            'return_code') == 'SUCCESS' else ''
        if not wx_app_sub_mch_id:
            wx_app_flag = False
            msg_app_wx = ret.get('result_msg', '进件到微信APP支付出现未知错误,请联系客服!')
        else:
            add_wx_app_sub_mch_id(mch_id, cur, wx_app_sub_mch_id, update_at)

    elif mch_wx_app_payment and (wx_ali_id[2] == 2):
        # 使用渠道商微信支付(APP支付)
        ret = get_dt_wx_app_pay_info(mch_id, cur)
        if ret[0]:
            update_mch_wx_app_pay_info(mch_id, cur, ret)
        else:
            wx_app_flag = False
    wx_app = [wx_app_flag, msg_app_wx]
    return wx_app


def mch_inlet_to_ali_reg(mch_id, cur, ali_flag, mch_ali_payment, wx_ali_id, mch_inlet_info,
                         alipay_category_id, update_at):
    msg_ali = "success"
    if mch_ali_payment and not wx_ali_id[1]:
        ret = create_alipay_sub_mch_id(mch_id,
                                       mch_inlet_info, alipay_category_id)
        save_mch_inlet_to_ali(mch_id, cur, ret, update_at)
        ali_sub_mch_id = ret.get(
            'sub_merchant_id') if ret.get(
            'code') in ['10000', 10000] else ''
        if not ali_sub_mch_id:
            ali_flag = False
            msg_ali = ret.get('sub_msg', '进件到支付宝发生未知错误,请联系客服!')
        else:
            add_ali_sub_mch_id(mch_id, cur, ali_sub_mch_id, update_at)
    ali_reg = [ali_flag, msg_ali]
    return ali_reg


def create_alipay_sub_mch_id(mch_id, mch_inlet_info, category_id):
    data = mch_inlet_to_alipay_data(
        mch_id=mch_id, mch_name=mch_inlet_info[0],
        mch_shortname=mch_inlet_info[1],
        service_phone=mch_inlet_info[2],
        category_id=category_id
    )
    ali_mch_info = urllib.urlencode(data)
    http_client = HTTPClient()
    response = http_client.fetch(
        "https://openapi.alipay.com/gateway.do",
        method='POST', body=ali_mch_info)
    ret = json.loads(response.body.decode('gbk'))
    log.detail.info(response.body.decode('gbk'))
    ali_ret = ret.get('alipay_boss_prod_submerchant_create_response', None)
    return ali_ret


def save_mch_inlet_to_wx(mch_id, cursor, ret, create_at):
    query = """insert into
              mch_inlet_to_wx_info (
              mch_id, return_code, return_msg,
              result_code, result_msg, create_at)
              values (%s, %s, %s, %s, %s, %s);"""
    cursor.execute(
        query,
        (
            mch_id,
            ret.get('result_code', 'FAIL'),
            ret.get('return_msg', 'FAIL'),
            ret.get('result_code', 'FAIL'),
            ret.get('result_msg', 'FAIL'),
            create_at
        )
    )


def save_mch_inlet_to_ali(mch_id, cursor, ret, create_at):
    query = """insert into
                  mch_inlet_to_wx_info (
                  mch_id, return_code, return_msg,
                  result_code, result_msg, create_at)
                  values (%s, %s, %s, %s, %s, %s);"""
    cursor.execute(
        query,
        (
            mch_id,
            ret.get('code', 'FAIL'),
            ret.get('msg', 'FAIL'),
            ret.get('sub_code', 'FAIL'),
            ret.get('sub_msg', 'FAIL'),
            create_at
        )
    )


def add_wx_app_sub_mch_id(mch_id, cursor, wx_app_sub_mch_id, update_at):
    query = """update mch_user set wx_app_sub_mch_id=%s,update_at=%s where mch_id=%s"""
    cursor.execute(query, (wx_app_sub_mch_id,
                           update_at, mch_id))


def add_ali_sub_mch_id(mch_id, cursor, ali_sub_mch_id, update_at):
    query = """update mch_user set ali_sub_mch_id=%s,
    update_at=%s where mch_id=%s"""
    cursor.execute(query, (ali_sub_mch_id,
                           update_at, mch_id))


def update_mch_user(mch_id, cursor, status, update_at):
    query = """update mch_user set status=%s,update_at=%s where mch_id=%s"""
    cursor.execute(query, (status, update_at, mch_id))


def auth_mch_inlet(mch_id, cursor, auth_status, update_at):
    query = """update mch_inlet_info set
        auth_status=%(auth_status)s,
        update_at=%(update_at)s where mch_id=%(mch_id)s"""
    cursor.execute(query, {
        'auth_status': auth_status,
        'update_at': update_at,
        'mch_id': mch_id
    })


def add_auth_inlet_info(mch_id, cursor, status, create_at):
    auth_user = get_bk_email(cursor)
    query = """
        insert into auth_mch_info (
        mch_id, comment, auth_user, auth_status, create_at)
        values (%s, %s, %s, %s, %s);"""
    cursor.execute(
        query,
        (
            mch_id,
            AUTH_STATUS[str(status)],
            auth_user,
            status,
            create_at
        )
    )


def get_bk_email(cursor):
    current_user = '10000001'
    query = """select email from bk_user where bk_id=%s"""
    cursor.execute(query, (current_user,))
    ret = cursor.fetchone()
    return ret[0]


def authed_wx_sub_mch(mch_id, cursor):
    query = """
        select auth_status from auth_mch_info
        where mch_id=%s
        ORDER BY id DESC
        LIMIT 1;
    """
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    if ret[0] == 2:
        return True
    else:
        return False


def update_wx_mch(mch_id, wx_use_parent, cursor, update_at):
    """更新微信端商户信息"""
    wx_use_parent = True if wx_use_parent in [2, '2'] else False
    mch_is_authed = authed_wx_sub_mch(mch_id, cursor)

    if (not wx_use_parent) and (not mch_is_authed):
        wx_mch_inlet_info = get_update_wx_sub_info(mch_id, cursor)
        ret = update_wx_sub_mch_id(
            wx_mch_inlet_info, APPID, WX_MCH_ID, WXPAY_KEY,
            WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        log.exception.info('reg:{}'.format(ret))
        save_mch_inlet_to_wx(mch_id, cursor, ret, update_at)


def add_fail_auth_inlet_info(mch_id, cursor, msg, create_at):
    auth_user = get_bk_email(cursor)
    query = """
        insert into auth_mch_info (
        mch_id, comment, auth_user, auth_status, create_at)
        values (%s, %s, %s, 3, %s);"""
    cursor.execute(
        query,
        (
            mch_id,
            msg,
            auth_user,
            create_at
        )
    )

# 查询审核进件信息表最新审核状态


def latest_status(mch_id, cursor):
    query = """
        SELECT auth_status, auth_user
        from auth_mch_info where mch_id = %s
         order by create_at desc
         LIMIT 1;"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def mch_inlet_to_alipay_data(mch_id, mch_name, mch_shortname, service_phone, category_id):
    biz_content = {
        "external_id": mch_id,
        "name": mch_name,
        "alias_name": mch_shortname,
        "service_phone": service_phone,
        "category_id": category_id,
        "source": ALI_PID,

    }

    common_params = {
        "app_id": ALI_APPID,
        "method": "alipay.boss.prod.submerchant.create",
        "charset": "utf-8",
        "sign_type": "RSA",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "biz_content": json.dumps(biz_content)
    }
    rsa_sign = AliRSAEncryptionClass(common_params)
    sign = rsa_sign.sign()
    common_params['sign'] = sign
    return common_params


def create_wx_sub_mch_id(mch_id, mch_inlet_info, PPID, WX_MCH_ID, WXPAY_KEY,
                         WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
    wx_business_no = mch_inlet_info[
        7] if mch_inlet_info[7] else mch_inlet_info[6]
    mchInletToWx = MerchantInletToWx(APPID, WX_MCH_ID, WXPAY_KEY)
    data = mchInletToWx.handle()(
        merchant_name=mch_inlet_info[0],
        merchant_shortname=mch_inlet_info[1],
        service_phone=mch_inlet_info[2],
        contact=mch_inlet_info[3],
        contact_phone=mch_inlet_info[4],
        contact_email=mch_inlet_info[5],
        business=wx_business_no,
        merchant_remark=mch_id
    )
    http_client = HTTPClient()
    response = http_client.fetch(
        "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=add",
        method='POST',
        body=data,
        client_key=WX_PRIVATE_KEY,
        client_cert=WX_PUB_KEY,
        ca_certs=WX_ROOT_CA
    )
    ret = xml_to_dict(response.body).get('root')
    log.detail.info(response.body)
    if not ret:
        ret = dict(result_code='FAIL')
    return ret


def get_update_wx_sub_info(mch_id, cursor):
    query = """
        select mch_inlet_info.mch_shortname,
        mch_inlet_info.service_phone,
        mch_user.wx_sub_mch_id
        from
        mch_inlet_info
        inner join mch_user on mch_user.mch_id=mch_inlet_info.mch_id
        where mch_inlet_info.mch_id=%s;"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def update_wx_sub_mch_id(
        mch_inlet_info, APPID, WX_MCH_ID, WXPAY_KEY,
        WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
    mchInletToWx = UpdateMerchantInletToWx(APPID, WX_MCH_ID, WXPAY_KEY)
    data = mchInletToWx.handle()(
        merchant_shortname=mch_inlet_info[0],
        service_phone=mch_inlet_info[1],
        sub_mch_id=mch_inlet_info[2],
    )
    http_client = HTTPClient()
    response = http_client.fetch(
        "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=modify",
        method='POST', body=data,
        client_key=WX_PRIVATE_KEY,
        client_cert=WX_PUB_KEY, ca_certs=WX_ROOT_CA
    )
    ret = xml_to_dict(response.body).get('root')
    log.detail.info(response.body)
    if not ret:
        ret = dict(result_code='FAIL')
    return ret


def get_dt_wx_pay_info(mch_id, cursor):
    query = """
        select
        dt_user.wx_sub_mch_id
        from dt_user
        inner join mch_inlet_info on dt_user.dt_id = mch_inlet_info.dt_id
        where mch_inlet_info.mch_id=%s;
    """
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def update_mch_wx_pay_info(mch_id, cursor, data):
    query = """
        update mch_user set wx_sub_mch_id=%s
        where mch_id=%s;
        """
    cursor.execute(query, (data[0], mch_id))


def get_dt_wx_app_pay_info(mch_id, cursor):
    query = """
            select
            dt_user.wx_app_sub_mch_id
            from dt_user
            inner join mch_inlet_info on dt_user.dt_id = mch_inlet_info.dt_id
            where mch_inlet_info.mch_id=%s;
        """
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def update_mch_wx_app_pay_info(mch_id, cursor, data):
    query = """
        update mch_user set wx_app_sub_mch_id=%s
        where mch_id=%s;
        """
    cursor.execute(query, (data[0], mch_id))


def automatic_activate(cursor, mch_id, update_at):
    payment_types = get_unactivated_payment_type(cursor, mch_id)
    activated_mch_payment(cursor, mch_id, 2, update_at)
    activated_mch_inlet(cursor, mch_id, 2, update_at)
    add_activated_mch_info(mch_id, cursor, payment_types, 2, update_at)
    return True


def notify_mch(cursor, mch_id, create_at):
    mch_info = get_mch_info(cursor, mch_id)
    count = is_send_email(cursor, mch_id)
    if not count:
        addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
        http_client = HTTPClient()
        data = {
            'env': env,
            'reciver': mch_info[0],
            'title': u'uline商户激活信息',
            'body': u"""
{1}，您好：
以下帐号重要信息请注意保密：
商户编号：{2}
登录帐号：{0}
初始登录密码：开户时填写的联系手机号 (登录后要求修改初始密码)
初始密钥：{3}
登陆地址：{4}
温馨提示：
请妥善保管您的账号及密码，为安全起见，新申请的账号，首次登录后请立即修改管理员密码.

广州优畅信息技术有限公司{5}
客服电话：4008047555""".format(str(mch_info[2]) + ".mch", mch_info[1], mch_info[2], mch_info[3], MCH_LOGIN_URL,
                          addition_info)
        }
        url = MESSAGE_URL + '/v1/email'
        response = http_client.fetch(url, body=json.dumps(data), method='POST')
        email = get_email(mch_id, cursor)
        if response.body == '1':
            save_activated_mch_email_info(cursor, mch_id, email, 'fail', 1, create_at)
        else:
            save_activated_mch_email_info(cursor, mch_id, email, 'success', 2, create_at)

    message_id = gen_randown_mch_pkey(8)
    tasks.callback_for_merchant_active.delay(mch_id, message_id)


def get_unactivated_payment_type(cursor, mch_id):
    query = """select payment_type from mch_payment where mch_id=%(mch_id)s and activated_status=1;"""
    cursor.execute(query, {"mch_id": mch_id})
    ret = cursor.fetchall()
    return ret


def get_email(mch_id, cursor):
    query = """select email from mch_user where mch_id=%s"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret[0]


def activated_mch_payment(cursor, mch_id, activated_status, update_at):
    query = """update mch_payment set
        activated_status=%(activated_status)s, update_at=%(update_at)s
        where mch_id=%(mch_id)s and activated_status=1"""
    cursor.execute(query, {
        "activated_status": activated_status,
        "mch_id": mch_id,
        "update_at": update_at
    })


def activated_mch_inlet(cursor, mch_id, activated_status, update_at):
    query = """update mch_inlet_info set
        activated_status=%(activated_status)s, update_at=%(update_at)s
        where mch_id=%(mch_id)s"""
    cursor.execute(query, {
        "activated_status": activated_status,
        "mch_id": mch_id,
        "update_at": update_at
    })


def add_activated_mch_info(mch_id, cursor, payment_types, activated_status, create_at):
    activated_user = get_bk_email(cursor)
    for _, payment_type in enumerate(payment_types):
        query = """insert into
            activated_mch_info (mch_id, payment_type, comment, activated_user, activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
        cursor.execute(query, (mch_id, payment_type,
                               ACTIVATED_STATUS[str(activated_status)
                                                ], activated_user, activated_status,
                               create_at))


def get_mch_info(cursor, mch_id):
    query = """select
            mch_inlet_info.email,
            mch_inlet_info.mch_name,
            mch_user.mch_id,
            mch_user.mch_pay_key
            from
            mch_user
            inner join mch_inlet_info on mch_inlet_info.mch_id=mch_user.mch_id
            where mch_user.mch_id=%s"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def is_send_email(cursor, mch_id):
    query = """select count(1) from activated_mch_email_info where mch_id=%s and status=2"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret[0]


def save_activated_mch_email_info(cursor, mch_id, email, comment, status, create_at):
    query = """insert into activated_mch_email_info (mch_id,email,comment,status,create_at)
               values (%s, %s, %s, %s, %s)"""
    cursor.execute(query, (mch_id, email, comment, status, create_at))


def get_dt_un_auth_mch(dt_id, offset=0):
    with db.get_db() as cur:
        sql = """select mch_id from mch_inlet_info where dt_id=%s and auth_status=1 and mch_id>%s
                order by mch_id limit 100 ;"""
        cur.execute(sql, (dt_id, offset))
        mch_ids = cur.fetchall()
        return mch_ids


def get_mch_change_record(cur, mch_id):
    sql = """select mch_id from change_record where mch_id=%s;"""
    cur.execute(sql, (mch_id,))
    result = cur.fetchone()
    return result


if __name__ == '__main__':
    # mch_ids = [100000147767]
    dt_id = 10000078823
    mch_ids = get_dt_un_auth_mch(dt_id)
    print len(mch_ids)
    if mch_ids:
        mch_ids = [mch_id[0] for mch_id in mch_ids]
        automatic_review(mch_ids)
