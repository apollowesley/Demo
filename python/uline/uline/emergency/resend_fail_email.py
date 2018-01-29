#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import argparse
from tornado import gen, ioloop
from uline.backend.__init__ import *


from uline.public.db import initdb
from uline.model.uline.base import uline_session
from uline.model.uline.base import ActivatedMchEmailInfo
import json
import time

from tornado.httpclient import HTTPClient
from uline.settings import env, MCH_LOGIN_URL, MESSAGE_URL
from tornado import gen, ioloop

from uline.public import log

reload(sys)
sys.setdefaultencoding('utf8')

# before_time 表示重发多久前的邮件(比如1h，表示重发1h内失败的邮件）


def get_send_fail_email(before_time):
    return uline_session.query(ActivatedMchEmailInfo.mch_id, ActivatedMchEmailInfo.email).\
        filter(ActivatedMchEmailInfo.comment == 'fail', ActivatedMchEmailInfo.create_at >= before_time).all()


def resend_email(fail_emails):
    resend_fail = []
    with db.get_db() as cur:
        for mch_id, email in fail_emails:
            log.uline_script.info(u'mch_id:%s | email:%s' % (mch_id, email))
            send_status = notify_mch(cur, mch_id, email, datetime.datetime.now())
            if not send_status:
                resend_fail.append(mch_id)
    return resend_fail


def get_mch_info(cursor, mch_id):
    query = """select
            mch_inlet_info.email,
            mch_inlet_info.mch_name,
            mch_user.mch_id,
            mch_user.mch_pay_key,
            mch_user.mch_pay_key,
            mch_inlet_info.cs_id
            from
            mch_user
            inner join mch_inlet_info on mch_inlet_info.mch_id=mch_user.mch_id
            where mch_user.mch_id=%s"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret


def notify_mch(cursor, mch_id, email, create_at):
    mch_info = get_mch_info(cursor, mch_id)
    count = is_send_email(cursor, mch_id)
    if not count:
        for i in range(3):
            addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
            http_client = HTTPClient()
            if mch_info[5]:
                body = u"""
{1}，您好：
以下帐号重要信息请注意保密：
门店编号：{2}
初始密钥：{3}

广州优畅信息技术有限公司{5}
客服电话：4008047555""".format(mch_info[0], mch_info[1], mch_info[2], mch_info[3], MCH_LOGIN_URL,
                          addition_info)
            else:

                body = u"""
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
            data = {
                'env': env,
                'reciver': mch_info[0],
                'title': u'uline商户激活信息',
                'body': body
            }
            url = MESSAGE_URL + '/v1/email'
            response = http_client.fetch(url, body=json.dumps(data), method='POST')
            print response.body, type(response.body)

            if response.body == '1':
                log.uline_script.info(u'send_fail|mch_id:%s|email:%s' % (mch_id, email))
                # 发送邮件过快可能被拒绝
                if i == 1:
                    time.sleep(3)
                else:
                    time.sleep(50)
            else:
                log.uline_script.info(u'send_success|mch_id:%s|email:%s' % (mch_id, email))
                save_activated_mch_email_info(cursor, mch_id, email, 'success', 2, create_at)
                return True
        else:
            save_activated_mch_email_info(cursor, mch_id, email, 'fail', 1, create_at)
            return False
    return True

    # 暂时没有商户反映回调激活出问题，先注释
    # message_id = gen_randown_mch_pkey(8)
    # tasks.callback_for_merchant_active.delay(mch_id, message_id)


def is_send_email(cursor, mch_id):
    query = """select count(1) from activated_mch_email_info where mch_id=%s and status=2"""
    cursor.execute(query, (mch_id,))
    ret = cursor.fetchone()
    return ret[0]


def save_activated_mch_email_info(cursor, mch_id, email, comment, status, create_at):
    query = """insert into activated_mch_email_info (mch_id,email,comment,status,create_at)
               values (%s, %s, %s, %s, %s)"""
    cursor.execute(query, (mch_id, email, comment, status, create_at))


def get_resend_time():
    """从命令行重发邮件时间"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('resend_time', metavar='RESEND_TIME', type=int,
                        help='input resend_time(s)')
    args = parser.parse_args()
    return args.resend_time


def send_alarm_email(fail_emails, resend_fail):
    http_client = HTTPClient()
    data = {
        'env': env,
        'reciver': '312736700@qq.com',
        'title': u'uline邮件发送失败商户超过一定数量',
        'body': str('fail_emails:%s | resend_fail:%s ' % (fail_emails, resend_fail))
    }
    url = MESSAGE_URL + '/v1/email'

    for i in range(3):

        response = http_client.fetch(url, body=json.dumps(data), method='POST')
        print response.body

        if response.body == '1':
            time.sleep(50)
        else:
            break


@gen.coroutine
def main():
    """
    获取发送失败的记录
    """
    now = datetime.datetime.now()
    print now
    delta = get_resend_time()
    print delta
    before_time = now - datetime.timedelta(seconds=delta)
    print before_time
    log.uline_script.info(u'获取获取发送失败的记录')
    fail_emails = set(get_send_fail_email(before_time))
    print fail_emails

    """
    根据mch_id和邮箱重发邮件
    """
    resend_fail = resend_email(fail_emails)

    if len(fail_emails) > 30 and len(resend_fail) > 2:
        send_alarm_email(fail_emails, resend_fail)


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
