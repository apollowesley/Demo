# -*- coding: utf-8 -*-
import json
import logging
import os
import time
import traceback
from datetime import datetime

from tornado import gen, ioloop
from tornado.httpclient import HTTPClient

from uline.backend import tasks
from uline.backend.__init__ import *
from uline.public import common, log, constants
from uline.public.common import gen_randown_mch_pkey
from uline.public.constants import AUTH_STATUS, ACTIVATED_STATUS
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA, ALI_PID, ALI_APPID, )
from uline.settings import env, MCH_LOGIN_URL, MESSAGE_URL
from uline.utils.alipay.get_code_by_name import query_code_by_name
from uline.utils.alipay.merchantInletToAlipay import AliRSAEncryptionClass
from uline.utils.alipay.query_alipay import create_alipay_mch_common
from uline.utils.alipay.query_alipay import create_alipay_mch_common_m1
from uline.utils.wxpay.merchantInletToWxV2 import MerchantInletToWx, UpdateMerchantInletToWx
from uline.utils.wxpay.util import xml_to_dict

logger = logging.getLogger('my_auto_review')
file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
filelog = logging.FileHandler(file_path + '/log/auto_review.log')
filelog.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filelog.setFormatter(formatter)
logger.addHandler(filelog)
logger.info('auto_review')


@gen.coroutine
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
                d0_mch = new_is_d0(mch_id, cur)
                if d0_mch:
                    logger.info('d0_mch:%s' % mch_id)
                    continue
                mch_inlet_info = get_mch_inlet_info(mch_id, cur)
                record = get_mch_change_record(cur, mch_id)
                # 进件逻辑

                mch_wx_payment = get_mch_payment(mch_id, cursor=cur, pay_type='weixin')
                mch_wx_app_payment = get_mch_payment(mch_id, cursor=cur, pay_type='weixin', wx_app=True)
                mch_ali_payment = get_mch_payment(mch_id, cursor=cur, pay_type='alipay')

                db_payments = get_all_db_payments(cur, mch_id)
                db_payments_paytypes = list()
                for each_payment in db_payments:
                    db_payments_paytypes.append(each_payment[0])

                change_record = get_update_changes(cur, mch_id)
                changed_withdraw = change_record.get('role', {})
                if changed_withdraw:
                    logger.info('d0_mch:%s' % mch_id)
                    continue

                changed_payments = change_record.get('payment', {})
                for payment_type in changed_payments:
                    payment = changed_payments[payment_type]
                    payment_type = int(payment.get('pay_type', 0))
                    action_type = payment.get('action_type', 2)
                    if action_type == 1:
                        db_payments_paytypes.append(payment_type)
                    elif action_type == 2 and payment_type not in db_payments_paytypes:
                        db_payments_paytypes.append(payment_type)
                    elif action_type == 3:
                        db_payments_paytypes.remove(payment_type)

                is_d0_mch = False
                for payment_type in db_payments_paytypes:
                    if payment_type in constants.OFFLINE_D1_WX_PAY_TYPES + constants.OFFLINE_D0_WX_PAY_TYPES:
                        mch_wx_payment = True
                    if payment_type in constants.ONLINE_D1_WX_PAY_TYPES + constants.ONLINE_D0_WX_PAY_TYPES:
                        mch_wx_app_payment = True
                    if payment_type in constants.D1_ALI_PAY_TYPES + constants.D0_ALI_PAY_TYPES:
                        mch_ali_payment = True
                    if payment_type in constants.D0_PAY_TYPES:
                        is_d0_mch = True

                # 只审核非d0商户
                if is_d0_mch:
                    continue

                wx_ali_id = get_mch_user_wx_ali_id(mch_id, cur)

                alipay_category_id = get_mch_alipay_category_id(mch_id, cur)

                wx_channel_id = None
                wx_app_channel_id = None

                if mch_wx_payment or mch_wx_app_payment:
                    wx_channel_id, wx_app_channel_id = get_dt_wx_channelid(mch_id, cur)

                wx_flag, msg_wx = mch_inlet_to_wx_reg(
                    mch_id, cur, wx_flag, mch_wx_payment, wx_ali_id, mch_inlet_info, wx_channel_id, update_at)
                wx_app_flag, msg_app_wx = mch_inlet_to_wx_app(
                    mch_id, cur, wx_app_flag, mch_wx_app_payment, wx_ali_id, mch_inlet_info, wx_app_channel_id,
                    update_at)
                ali_flag, msg_ali = yield mch_inlet_to_ali_reg(
                    mch_id, cur, ali_flag, mch_ali_payment, wx_ali_id, mch_inlet_info, alipay_category_id, update_at)

                if not (wx_flag and wx_app_flag and ali_flag):
                    comment_news = [msg_wx, msg_app_wx, msg_ali]
                    field = ["微信支付进件:{}", "微信APP进件:{}", "支付宝进件:{}"]
                    show_comment = " ".join(
                        _f.format(_com) for _f, _com in zip(field, comment_news) if _com != "success")
                    add_fail_auth_inlet_info(mch_id, cur, show_comment, update_at)
                    auth_status = 3
                    mch_status = 1
                    failed_inlet_3party.append(mch_id)
                    logger.info("进件到微信、支付宝失败：{},{}".format(mch_id, show_comment))
                    record_utils_rollback(mch_id, cur)
                    auth_mch_inlet(mch_id, cur, auth_status, update_at)

                else:
                    mch_status = 2
                    auth_status = 2
                    update_mch_user(mch_id, cur, mch_status, update_at)
                    auth_mch_inlet(mch_id, cur, auth_status, update_at)

                    # 修改微信端商户信息(包括商户简称和服务电话)
                    # update_wx_mch(mch_id, wx_ali_id[2], cur, update_at)

                    add_auth_inlet_info(mch_id, cur, auth_status, update_at)

                    result = update_changes(mch_id, cur, update_at)
                    db_payments = get_all_db_payments(cur, mch_id)
                    has_wx_d0 = False
                    has_dine = False
                    for each_payment in db_payments:
                        payment_type = each_payment[0]
                        if payment_type in constants.OFFLINE_D0_WX_PAY_TYPES + constants.ONLINE_D0_WX_PAY_TYPES:
                            has_wx_d0 = True
                        if payment_type in constants.DINNER_TOGGETHER_PAY_TYPES:
                            has_dine = True
                    if not has_wx_d0:
                        # 如果是没有微信D0支付方式
                        sql = """update d0_withdraw_fee set wx=%s where role=%s and role_type='mch'"""
                        cur.execute(sql, (None, mch_id))
                    if not has_dine:
                        # 费围餐，删除扩展项，暂时只有围餐的扩展信息，删除全部
                        sql = """delete from role_info_extension where role_id=%s and role_type=%s"""
                        cur.execute(sql, (mch_id, 'mch'))

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
                    # 解决进件微信支付宝失败 回调信息仍然返回2（成功）的bug
                    if not (wx_flag and wx_app_flag and ali_flag):
                        mch_status = 1
                    else:
                        mch_status = 2
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
        tasks.callback_for_merchant_status.apply_async((mch_id, mch_status, message_id), )

        if has_active_payments:
            # 激活支付方式后通知商户
            with db.get_db() as cur:
                notify_mch(cur, mch_id, update_at)
                print('激活：%s' % mch_id)

        if mch_status == 2:
            logger.info("进件成功，{}".format(mch_id))

    if failed_inlet_3party:
        logger.info("进件到微信或支付宝失败的商户:{}".format(failed_inlet_3party))

    raise gen.Return(True)


def get_dt_wx_channelid(mch_id, cursor):
    sql = """select dt_inlet_info.wx_channel_id, dt_inlet_info.wx_app_channel_id
             from dt_inlet_info inner join mch_inlet_info on dt_inlet_info.dt_id = mch_inlet_info.dt_id
             where mch_inlet_info.mch_id=%s;"""
    cursor.execute(sql, (mch_id,))
    result = cursor.fetchone()
    wx_channel_id = None
    wx_app_channel_id = None
    if result:
        wx_channel_id = result[0]
        wx_app_channel_id = result[1]
    return wx_channel_id, wx_app_channel_id


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


def is_d0(mch_id, cursor=None):
    query = """select 1 from mch_payment where payment_type > 100 and mch_id = %s;"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return True if ret else False


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
            address,
            province,
            city,
            district,
            cs_id
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


def mch_inlet_to_wx_reg(mch_id, cur, wx_flag, mch_wx_payment, wx_ali_id, mch_inlet_info, wx_channel_id, update_at):
    # 微信支付(扫码支付／刷卡支付／公众账号支付)
    msg_wx = "success"

    app_id = APPID
    wx_mch_id = WX_MCH_ID
    wx_pay_key = WXPAY_KEY
    wx_private_key = WX_PRIVATE_KEY
    wx_pub_key = WX_PUB_KEY
    wx_root_ca = WX_ROOT_CA

    if mch_wx_payment and not wx_ali_id[0]:
        ret = create_wx_sub_mch_id(mch_id, mch_inlet_info, app_id, wx_mch_id, wx_pay_key,
                                   wx_private_key, wx_pub_key, wx_root_ca, wx_channel_id)
        time.sleep(5)
        log.exception.info('reg:{}'.format(ret))

        save_mch_inlet_to_wx(mch_id, cur, ret, update_at)

        default_err_msg = '进件到微信APP支付出现未知错误,请联系客服!'
        wx_sub_mch_id, msg_wx = deal_with_wx_result(ret, 'sub_mch_id', default_err_msg)
        if wx_sub_mch_id:
            add_wx_sub_mch_id(mch_id, cur, wx_sub_mch_id, update_at)
        else:
            wx_flag = False

    elif mch_wx_payment and wx_ali_id[0]:
        # 修改微信端商户信息(包括商户简称和服务电话)
        changes = get_update_changes(cur, mch_id)
        update_wx_mch(mch_id, wx_ali_id[2], cur, changes=changes)

    wx_reg = [wx_flag, msg_wx]
    return wx_reg


def add_wx_sub_mch_id(mch_id, cursor, wx_sub_mch_id, update_at):
    query = """update mch_user set wx_sub_mch_id=%s,update_at=%s where mch_id=%s"""
    cursor.execute(query, (wx_sub_mch_id,
                           update_at, mch_id))


def mch_inlet_to_wx_app(mch_id, cur, wx_app_flag, mch_wx_app_payment, wx_ali_id, mch_inlet_info, wx_app_channel_id,
                        update_at):
    # 微信支付(APP支付)
    msg_app_wx = "success"
    if mch_wx_app_payment and not wx_ali_id[3]:
        ret = create_wx_sub_mch_id(mch_id,
                                   mch_inlet_info, WX_APP_APPID, WX_APP_MCH_ID, WXPAY_APP_KEY,
                                   WX_APP_PRIVATE_KEY, WX_APP_PUB_KEY, WX_APP_ROOT_CA, wx_app_channel_id)
        log.exception.info('app:{}'.format(ret))
        save_mch_inlet_to_wx(mch_id, cur, ret, update_at)

        default_err_msg = '进件到微信APP支付出现未知错误,请联系客服!'

        wx_app_sub_mch_id, msg_app_wx = deal_with_wx_result(ret, 'sub_mch_id', default_err_msg)

        if wx_app_sub_mch_id:
            add_wx_app_sub_mch_id(mch_id, cur, wx_app_sub_mch_id, update_at)
        else:
            wx_app_flag = False

    wx_app = [wx_app_flag, msg_app_wx]
    return wx_app


@gen.coroutine
def mch_inlet_to_ali_reg(mch_id, cur, ali_flag, mch_ali_payment, wx_ali_id, mch_inlet_info,
                         alipay_category_id, update_at):
    msg_ali = "success"
    if mch_ali_payment:
        ret = yield create_alipay_sub_mch_id(mch_id,
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
    # return ali_reg
    raise gen.Return(ali_reg)


@gen.coroutine
def create_alipay_sub_mch_id(mch_id, mch_inlet_info, category_id):
    # data = mch_inlet_to_alipay_data(
    #     mch_id=mch_id, mch_name=mch_inlet_info[0],
    #     mch_shortname=mch_inlet_info[1],
    #     service_phone=mch_inlet_info[2],
    #     category_id=category_id
    # )
    #
    # ali_mch_info = urllib.urlencode(data)
    # http_client = HTTPClient()
    # response = http_client.fetch(ALI_SERVER_ADDRESS,
    #                              method='POST', body=ali_mch_info)
    # ret = json.loads(response.body.decode('gbk'))
    # log.detail.info(response.body.decode('gbk'))
    # ali_ret = ret.get('alipay_boss_prod_submerchant_create_response', None)
    # return ali_ret

    query_dict = {'external_id': mch_id, 'name': mch_inlet_info[0], 'alias_name': mch_inlet_info[1],
                  'service_phone': mch_inlet_info[2],
                  'category_id': category_id,
                  }
    level = 'M1'
    # 如果有填区域信息，则以M2等级进件
    if mch_inlet_info[-2]:
        province_code, city_code, district_code = query_code_by_name(mch_inlet_info[-4], mch_inlet_info[-3],
                                                                     mch_inlet_info[-2])
        if province_code and city_code and district_code:
            query_dict['address_info'] = [{
                'province_code': province_code,
                'city_code': city_code,
                'district_code': district_code,
                'address': mch_inlet_info[-5],
                'type': 'BUSINESS_ADDRESS'
            }]
            level = 'M2'
    if level == 'M2':
        ali_ret = yield create_alipay_mch_common(query_dict)
    else:
        ali_ret = yield create_alipay_mch_common_m1(query_dict)
    raise gen.Return(ali_ret)


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


def update_wx_mch(mch_id, wx_use_parent, cursor, changes=None):
    """更新微信端商户信息"""
    wx_use_parent = True if wx_use_parent in [2, '2'] else False
    mch_is_authed = authed_wx_sub_mch(mch_id, cursor)

    app_id = APPID
    wx_mch_id = WX_MCH_ID
    wx_pay_key = WXPAY_KEY
    wx_private_key = WX_PRIVATE_KEY
    wx_pub_key = WX_PUB_KEY
    wx_root_ca = WX_ROOT_CA

    if (not wx_use_parent) and (not mch_is_authed):
        wx_mch_inlet_info = get_update_wx_sub_info(mch_id, cursor)

        # 如果有修改记录，使用修改记录的数据
        wx_mch_info = list(wx_mch_inlet_info)
        if changes:
            if 'mch_shortname' in changes:
                wx_mch_info[0] = changes['mch_shortname']
            if 'service_phone' in changes:
                wx_mch_info[1] = changes['service_phone']

        ret = update_wx_sub_mch_id(
            wx_mch_info, app_id, wx_mch_id, wx_pay_key,
            wx_private_key, wx_pub_key, wx_root_ca)
        log.exception.info('reg:{}'.format(ret))
        save_mch_inlet_to_wx(mch_id, cursor, ret, common.timestamp_now())


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


def create_wx_sub_mch_id(mch_id, mch_inlet_info, app_id, wx_mch_id, wx_pay_key,
                         wx_private_key, wx_pub_key, wx_root_ca, channel_id):
    wx_business_no = mch_inlet_info[
        7] if mch_inlet_info[7] else mch_inlet_info[6]
    mchInletToWx = MerchantInletToWx(app_id, wx_mch_id, wx_pay_key)
    inlet_data = {
        'merchant_name': mch_inlet_info[0],
        'merchant_shortname': mch_inlet_info[1],
        'service_phone': mch_inlet_info[2],
        'contact': mch_inlet_info[3],
        'contact_phone': mch_inlet_info[4],
        'contact_email': mch_inlet_info[5],
        'business': wx_business_no,
        'merchant_remark': mch_id
    }
    if channel_id:
        inlet_data['channel_id'] = channel_id

    log.detail.info('inlet_data:%s' % inlet_data)
    data = mchInletToWx.handle()(**inlet_data)
    log.detail.info('mchInletToWx|data:%s' % data)

    # 兼容现有api
    http_client = HTTPClient()
    response = http_client.fetch(
        "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=add",
        method='POST',
        body=data,
        client_key=wx_private_key,
        client_cert=wx_pub_key,
        ca_certs=wx_root_ca
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


def update_wx_sub_mch_id(mch_inlet_info, app_id, wx_mch_id, wx_pay_key,
                         wx_private_key, wx_pub_key, wx_root_ca):
    mchInletToWx = UpdateMerchantInletToWx(app_id, wx_mch_id, wx_pay_key)
    data = mchInletToWx.handle()(
        merchant_shortname=mch_inlet_info[0],
        service_phone=mch_inlet_info[1],
        sub_mch_id=mch_inlet_info[2],
    )
    http_client = HTTPClient()
    response = http_client.fetch(
        "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=modify",
        method='POST', body=data,
        client_key=wx_private_key,
        client_cert=wx_pub_key, ca_certs=wx_root_ca
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
        email = get_email(mch_id, cursor)
        for i in range(3):
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
客服电话：4008047555""".format(mch_info[2] + ".mch", mch_info[1], mch_info[2], mch_info[3], MCH_LOGIN_URL,
                          addition_info)
            }
            url = MESSAGE_URL + '/v1/email'
            response = http_client.fetch(url, body=json.dumps(data), method='POST')

            if response.body == '1':
                # 自动审核时，发送邮件过快可能被拒绝
                if i == 1:
                    time.sleep(3)
                else:
                    time.sleep(50)
            else:
                save_activated_mch_email_info(cursor, mch_id, email, 'success', 2, create_at)
                break
        else:
            save_activated_mch_email_info(cursor, mch_id, email, 'fail', 1, create_at)

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


def get_dt_un_auth_mch(dt_id):
    with db.get_db() as cur:
        sql = """select mch_id from mch_inlet_info where dt_id=%s and auth_status='1';"""
        cur.execute(sql, (dt_id,))
        mch_ids = cur.fetchall()
        return [mch_id[0] for mch_id in mch_ids]


def get_mch_change_record(cur, mch_id):
    sql = """select mch_id from change_record where mch_id=%s;"""
    cur.execute(sql, (mch_id,))
    result = cur.fetchone()
    return result


def update_mch_payments(mch_id, cur, payments):
    changed_payments = dict()
    if isinstance(payments, list):
        for each_payment in payments:
            changed_payments[each_payment[0]] = {'pay_type': each_payment[0],
                                                 'pay_rate': each_payment[1], 'pre_status': each_payment[2]}
    else:
        changed_payments = payments
    for paytype in changed_payments:
        record = changed_payments[paytype]
        payment_type = record['pay_type']
        payment_rate = record['pay_rate']
        exist_status = record['pre_status']
        action_type = record.get('action_type', 2)

        # action_type 动作，1：新增，2：更新，3: 删除
        if action_type == 2:
            activated_status = 1
            mch_id = mch_id
            # 查询支付方式的原有费率，如果有且等于更新的费率，则需要还原为原有的激活状态
            sql = """select activated_status, payment_rate from mch_payment where mch_id=%s and payment_type=%s;"""
            cur.execute(sql, (mch_id, payment_type))
            result = cur.fetchone()
            # 如果在数据库中已经存在
            if result:
                exist_rate = result[1]
                # 如果费率前后相等，则不用修改费率，状态还原为原有的状态（为兼容已有的数据）
                if exist_rate and exist_rate == payment_rate:
                    activated_status = exist_status

                # 更新支付费率的信息
                sql = """update mch_payment set payment_type=%s, payment_rate=%s, activated_status=%s
                                             where mch_id=%s and payment_type=%s;"""
                cur.execute(sql, (payment_type, payment_rate,
                                  activated_status, mch_id, payment_type))
        elif action_type == 1:
            sql = """INSERT INTO mch_payment(mch_id, payment_type, payment_rate, activated_status, create_at, update_at)
                                VALUES (%s, %s, %s, %s, %s, %s);"""
            cur.execute(sql, (mch_id, payment_type, payment_rate, 1, datetime.now(), datetime.now()))
        elif action_type == 3:
            sql = """DELETE FROM mch_payment WHERE mch_id=%s and payment_type=%s;"""
            cur.execute(sql, (mch_id, payment_type))


def update_mch_balance_info(mch_id, cur, change_balance_info):
    """
    更新结算账户信息
    :param cur: 数据库相关游标
    :param change_balance_info: dict，需要修改的信息
    """
    sql = """update mch_balance set """
    update_colums = []
    params_values = []
    for key in change_balance_info:
        update_colums.append("""{}=%s""".format(key))
        params_values.append(change_balance_info[key])
    sql = sql + ','.join(update_colums)
    where_str = " where mch_id=%s;"
    sql = sql + where_str
    params_values.append(mch_id)
    cur.execute(sql, tuple(params_values))


def update_mch_inlet_info(mch_id, cur, change_inlet_info):
    sql = """update mch_inlet_info set """
    update_colums = []
    params_values = []
    for key in change_inlet_info:
        update_colums.append("""{}=%s""".format(key))
        params_values.append(change_inlet_info[key])
    sql = sql + ','.join(update_colums)
    where_str = " where mch_id=%s;"
    sql = sql + where_str
    params_values.append(mch_id)
    cur.execute(sql, tuple(params_values))


def update_mch_inlet_active_status(mch_id, cur):
    """更新商户进件激活状态
    """
    # 查看所有的支付状态
    inlet_activated_status = 1
    sql = """select activated_status from mch_payment where mch_id=%s;"""
    cur.execute(sql, (mch_id,))
    all_paytment_status = cur.fetchall()
    for payment_status in all_paytment_status:
        paystatus = payment_status[0]
        if paystatus == 2:
            inlet_activated_status = 2
            break
    sql = """update mch_inlet_info set activated_status=%s where mch_id = %s;"""
    cur.execute(sql, (inlet_activated_status, mch_id,))
    return inlet_activated_status


def update_changes(mch_id, cur, update_at):
    # 检查这个商户是否有变更金额
    sql = """select data_json from change_record where mch_id=%s and status=1;"""
    cur.execute(sql, (mch_id,))
    query_change_record_json = cur.fetchone()
    # 验证数据的合法性
    if query_change_record_json:
        query_change_record = json.loads(query_change_record_json[0])
        if isinstance(query_change_record, dict):
            # 取出所有需要生效的数据
            if 'payment' in query_change_record:
                payments = query_change_record['payment']
                update_mch_payments(mch_id, cur, payments)  # 修改变更记录表里面的状态

            if 'role' in query_change_record:
                update_withdrawinfo = query_change_record.get('role', {})
                if update_withdrawinfo:
                    update_withdraw_info(cur, mch_id, update_withdrawinfo)

            # 账户信息修改
            if 'balance_info' in query_change_record:
                balance_update_info = query_change_record['balance_info']
                update_keys = ['balance_type', 'balance_name', 'bank_no', 'balance_account',
                               'id_card_no']
                change_balance_info = {key: balance_update_info[key] for key in update_keys if
                                       key in balance_update_info}
                change_balance_info['update_at'] = update_at
                update_mch_balance_info(mch_id, cur, change_balance_info)

            need_update_keys = ["province", "city", "district", "license_period", "mobile", "mch_shortname",
                                "license_scope", "notify_url",
                                "mch_name", "service_phone", "contact", "license_num", "email", "address",
                                'id_card_img_f', 'id_card_img_b', 'license_img', 'license_start_date',
                                'license_end_date', 'dt_sub_id', 'u_ind_code', 'wx_ind_code', 'ali_ind_code']
            change_inlet_info = {key: query_change_record[key] for key in need_update_keys if
                                 key in query_change_record}

            if change_inlet_info:
                update_mch_inlet_info(mch_id, cur, change_inlet_info)

            update_extension_infos = ['mch_inner_img', 'mch_front_img', 'mch_desk_img']
            change_extensions = {key: query_change_record[key] for key in update_extension_infos if
                                 key in query_change_record}
            extension_sql = """SELECT extension_name, extension_value, id FROM role_info_extension
                                               WHERE role_id=%s and role_type='mch'
                                            """
            cur.execute(extension_sql, (mch_id,))
            extensions = dict()
            extensions_db = cur.fetchall()
            for each_extention in extensions_db:
                extensions[each_extention[0]] = each_extention
            for each_extention_name in change_extensions:
                change_value = change_extensions[each_extention_name]
                if each_extention_name in extensions:
                    if change_value and (change_value != extensions[each_extention_name]):
                        extension_id = extensions[each_extention_name][2]
                        sql = """UPDATE role_info_extension SET extension_value=%s,update_time=%s WHERE id=%s"""
                        cur.execute(sql, (change_value, datetime.now(), extension_id))
                else:
                    sql = """insert into role_info_extension
                                            (role_id, role_type, extension_name, extension_value, create_time, update_time)
                                        VALUES (%s,   %s,        %s,             %s,              %s,          %s)"""
                    cur.execute(sql, (
                        mch_id, 'mch', each_extention_name, change_value, datetime.now(), datetime.now()))

            query = """update change_record set status = %s, create_at = now() where mch_id = %s;"""
            cur.execute(query, (2, mch_id,))

        inlet_activated_status = update_mch_inlet_active_status(mch_id, cur)
        log.exception.info('mch_auth update payments success')
        # return inlet_activated_status
        return inlet_activated_status


def record_utils_rollback(mch_id, cur):
    # 先更新状态为驳回
    search_id = mch_id
    query = """update mch_payment set activated_status = %s where mch_id = %s and payment_type = %s;"""

    change_info = select_change_record(mch_id, cur)
    if not change_info:
        return True
    result = json.loads(change_info[1]).get('payment', dict())
    payments = {}
    # 兼容以前列表数据
    if isinstance(result, list):
        for each_payment in result:
            payment_info = dict()
            payment_info['pay_type'] = each_payment[0]
            payment_info['pre_status'] = each_payment[2]
            payments[each_payment[0]] = payment_info
    elif isinstance(result, dict):
        payments = result
    for payment_type in payments:
        payment = payments[payment_type]
        cur.execute(query, (payment['pre_status'], search_id, payment_type))

    update_change_record_status(mch_id, cur)
    return True


def update_change_record_status(mch_id, cur, status=3):
    query = """update change_record set status = %s, create_at = now() where mch_id = %s;"""
    cur.execute(query, (status, mch_id))


def select_change_record(mch_id, cur):
    query = """select mch_id, data_json from change_record
                where change_type = 2 and status = 1 and mch_id = %s;
                """
    cur.execute(query, (mch_id,))
    result = cur.fetchone()
    return result


def deal_with_wx_result(wx_result, result_key, default_error_msg):
    """
    处理微信反馈结果
    :param wx_result: 微信反馈的信息
    :param result_key: 需要的值的key
    :param default_error_msg: 默认错误信息，在微信没有相关字段时有用
    :return: (result, msg)分别对应需要的值和结果消息
    """
    return_code = wx_result.get("return_code", 'FAIL')
    result_code = wx_result.get("result_code", 'FAIL')
    SUCCESS_TAG = "SUCCESS"
    if return_code != SUCCESS_TAG:
        return None, wx_result.get('return_msg', default_error_msg)
    if result_code != SUCCESS_TAG:
        return None, wx_result.get('result_msg', default_error_msg)
    result = wx_result.get(result_key, None)
    msg = wx_result.get('result_msg', "OK")
    return result, msg


def get_all_db_payments(cursor, mch_id):
    query = """select payment_type from mch_payment where mch_id=%s"""
    cursor.execute(query, (mch_id,))
    return cursor.fetchall()


def get_update_changes(cur, mch_id):
    sql = """select data_json from change_record where mch_id=%s and status=1;"""
    cur.execute(sql, (mch_id,))
    query_change_record_json = cur.fetchone()
    # 验证数据的合法性
    if query_change_record_json:
        query_change_record = json.loads(query_change_record_json[0])
        if isinstance(query_change_record, dict):
            return query_change_record
    else:
        return {}


def update_withdraw_info(cursor, mch_id, update_withdrawinfo):
    action_type = update_withdrawinfo.get('action_type', 0)
    wx_withdraw = update_withdrawinfo.get('wx', None)
    alipay_withdraw = update_withdrawinfo.get('alipay', None)
    if action_type == 1:
        sql = """insert into d0_withdraw_fee(role, role_type, wx, alipay, create_at, update_at)
                                        VALUES (%s,      %s,     %s,  %s   ,  %s,       %s)"""
        cursor.execute(sql, (mch_id, 'mch', wx_withdraw, alipay_withdraw, datetime.now(), datetime.now()))
    elif action_type == 2:
        sql = """update d0_withdraw_fee set wx=%s,alipay=%s,update_at=%s where role=%s and role_type='mch'"""
        cursor.execute(sql, (wx_withdraw, alipay_withdraw, datetime.now(), mch_id))


def new_is_d0(mch_id, cursor=None):
    query = """select 1 from mch_payment where withdraw_rate is not null and withdraw_fee is not null and mch_id = %s;"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return True if ret else False


@gen.coroutine
def main():
    # mch_ids = [100000147767]
    # dt_id = 10000078823
    dt_ids = [10000005554, 10000006774, 10000063337, 10000050727, 10000037107, 10000045429, 10000056667]
    for dt_id in dt_ids:
        mch_ids = get_dt_un_auth_mch(dt_id)
        print len(mch_ids)
        if mch_ids:
            mch_ids = [mch_id[0] for mch_id in mch_ids]
            flag = yield automatic_review(mch_ids)


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(main)
