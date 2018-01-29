#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import datetime
import time
from tornado import gen, ioloop
from tornado.httpclient import HTTPClient, AsyncHTTPClient
from uline.backend import tasks
from uline.config.base import MESSAGE_URL
from uline.public.common import gen_randown_mch_pkey
from uline.public.constants import ACTIVATED_STATUS
from uline.settings import env, MCH_LOGIN_URL, AUTH_URL
from uline.backend.__init__ import *
from uline.public.db import initdb
from uline.public import log
from uline.utils.dayzero.form_verify import check_mch_is_d0


def get_dt_id_and_d0():
    """从命令行获取渠道商id"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dt_id', metavar='DT_ID', type=str,
                        help='input dt_id')
    parser.add_argument('-d0', metavar='D0', type=str,
                        help='input auth d0 or not(auth d0 input 1 else 0)', default=0)
    args = parser.parse_args()
    return args.dt_id, args.d0 if args.d0 else 0


def get_dt_id():
    """从命令行获取渠道商id"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dt_id', metavar='DT_ID', type=str,
                        help='input dt_id')
    args = parser.parse_args()
    return args.dt_id


def get_dt_un_auth_mch(dt_id):
    with db.get_db() as cur:
        sql = """select mch_id from mch_inlet_info where dt_id=%s and auth_status='1';"""
        cur.execute(sql, (dt_id,))
        mch_ids = cur.fetchall()
        return [mch_id[0] for mch_id in mch_ids]

    # mch_ids = uline_session.query(MchInletInfo.mch_id).filter(MchInletInfo.dt_id == dt_id,
    #                                                           MchInletInfo.auth_status == 1)
    # return set(mch_ids)


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


def get_email(mch_id, cursor):
    query = """select email from mch_user where mch_id=%s"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret[0]


def save_activated_mch_email_info(cursor, mch_id, email, comment, status, create_at):
    query = """insert into activated_mch_email_info (mch_id,email,comment,status,create_at)
               values (%s, %s, %s, %s, %s)"""
    cursor.execute(query, (mch_id, email, comment, status, create_at))


def get_unactivated_payment_type(cursor, mch_id):
    query = """select payment_type from mch_payment where mch_id=%(mch_id)s and activated_status=1;"""
    cursor.execute(query, {"mch_id": mch_id})
    ret = cursor.fetchall()
    return ret


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


def get_bk_email(cursor):
    current_user = '10000001'
    query = """select email from bk_user where bk_id=%s"""
    cursor.execute(query, (current_user,))
    ret = cursor.fetchone()
    return ret[0]


def add_activated_mch_info(mch_id, cursor, payment_types, activated_status, create_at):
    activated_user = get_bk_email(cursor)
    for _, payment_type in enumerate(payment_types):
        query = """insert into
            activated_mch_info (mch_id, payment_type, comment, activated_user, activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
        cursor.execute(query, (mch_id, payment_type,
                               ACTIVATED_STATUS[str(activated_status)
                                                ], activated_user, activated_status,
                               create_at))


def automatic_activate_for_mch_ids(mch_ids, update_at):
    with db.get_db() as cursor:
        for mch_id in mch_ids:
            payment_types = get_unactivated_payment_type(cursor, mch_id)
            activated_mch_payment(cursor, mch_id, 2, update_at)
            activated_mch_inlet(cursor, mch_id, 2, update_at)
            add_activated_mch_info(mch_id, cursor, payment_types, 2, update_at)
    return True


def callback_and_nofity_mch(mch_ids):
    # 不需要等待发送邮件成功才更新通知状态（邮件通知这里有重试机制，可能导致需要长时间等待）
    for mch_id in mch_ids:
        with db.get_db() as cur:
            notify_mch(cur, mch_id, datetime.datetime.now())

        with db.get_db() as cur:
            message_id = gen_randown_mch_pkey(8)
            tasks.callback_for_merchant_status.apply_async((mch_id, 2, message_id),)


def get_inlet_success_mch(mch_ids):
    with db.get_db() as cur:
        query = """select
            mch_inlet_info.mch_id
            from
            mch_inlet_info
            where mch_inlet_info.mch_id in %s and mch_inlet_info.auth_status=2"""
        cur.execute(query, (mch_ids,))
        ret = cur.fetchall()
        return ret


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
客服电话：4008047555""".format(str(mch_info[0]) + ".mch", mch_info[1], mch_info[2], mch_info[3], MCH_LOGIN_URL,
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


def new_check_mch_is_d0(mch_id):
    with db.get_db() as cursor:
        query = """select 1 from mch_payment where withdraw_rate is not null and withdraw_fee is not null and mch_id = %s;"""
        cursor.execute(query, (mch_id,))
        ret = cursor.fetchone()
        return True if ret else False


@gen.coroutine
def main():
    dt_id = get_dt_id()
    # auth_d0 = get_auth_d0_mch()
    # dt_id = '10000040700'
    bk_id = '10000001'
    fail = []
    success = []
    except_mch = []
    log.uline_script.info(u'dt_id:%s' % dt_id)
    if dt_id:
        mch_ids = get_dt_un_auth_mch(dt_id)
        http_client = AsyncHTTPClient()
        for mch_id in mch_ids:
            try:
                # 根据auth_d0和check_mch_is_d0判断是否需要审核
                if check_mch_is_d0(mch_id):
                    log.uline_script.info(u'd0 mch_id:%s does not auth' % mch_id)
                    continue
                log.uline_script.info(u'auth mch_id:%s' % mch_id)
                url = AUTH_URL + '/v1/mchauth'
                data = {'mch_id': mch_id, 'bk_id': bk_id}
                response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
                if response.body == '2':
                    # success
                    success.append(mch_id)

                else:
                    # fail
                    fail.append(mch_id)
            except:
                except_mch.append(mch_id)
        log.uline_script.info(u'success:%s' % success)
        log.uline_script.info(u'auth fail:%s' % fail)
        log.uline_script.info(u'except_mch fail:%s' % except_mch)
        # 添加默认等待时间10s
        time.sleep(10)
        # 对于审核通过的商户，激活并通知
        if success:
            # 查出进件成功的商户
            new_success = tuple([str(i) for i in success])
            inlet_success = get_inlet_success_mch(new_success)
            log.uline_script.info(u'inlet_success success:%s' % inlet_success)
            has_active_payments = automatic_activate_for_mch_ids(inlet_success, datetime.datetime.now())
            callback_and_nofity_mch(inlet_success)


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
