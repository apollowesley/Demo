# -*- coding: utf-8 -*-
import json
import urllib
import time
from datetime import datetime, timedelta
import logging
import os
import traceback
from tornado.httpclient import AsyncHTTPClient

from uline.settings import env, MCH_LOGIN_URL, MESSAGE_URL
from tornado import gen, ioloop
from uline.settings import DIST_LOGIN_URL


from uline.backend.__init__ import *


from uline.public import common, log


@gen.coroutine
def resend_dt_email(dt_id, cur):
    if 2 > 1:
        if 2 > 1:
            try:
                email = yield get_email(dt_id, cur)
                # yield activated_dt_payment(cur)
                # yield activated_dt_inlet(cur)
                # yield add_activated_dt_info(cur)
                dt_info = yield get_dt_info(dt_id, cur)
                print dt_info[0], dt_info[1], dt_info[2]
            except Exception as err:
                log.exception.info(err)
                cur.connection.rollback()
                log.uline_script.info(u'fail|dt_id:%s' % dt_id)
                # self.rsp = common.f_rsp(code=406, msg='fail')

        count = yield is_send_email(dt_id, cur)

        if not count:
            addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': dt_info[0],
                'title': u'uline渠道商激活信息',
                'body': u"""
{1}，您好：
以下帐号重要信息请注意保密：
优畅技术文档：http://docs.uline.cc
渠道商编号：{2}
登录帐号：{0}
初始登录密码：开户时填写的联系手机号 (登录后要求修改初始密码)
登陆地址：{3}
温馨提示：
请妥善保管您的账号及密码，为安全起见，新申请的账号，首次登录后请立即修改管理员密码.

广州优畅信息技术有限公司{4}
客服电话：4008047555""".format(str(dt_info[2]) + ".dt", dt_info[1].decode('utf-8'), dt_info[2], DIST_LOGIN_URL, addition_info)
            }
            url = MESSAGE_URL + '/v1/email'
            print data
            response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
            if response.body == '1':
                save_activated_dt_email_info(cur, dt_id, 'fail', 1, email)
            else:
                save_activated_dt_email_info(cur, dt_id, 'success', 2, email)


def save_activated_dt_email_info(cur, dt_id, comment, status, email):
    query = """insert into
              activated_dt_email_info (dt_id,email,comment,status,create_at)
              values (%s, %s, %s, %s, %s)"""
    cur.execute(query, (dt_id, email,
                        comment, status, datetime.now()))


@gen.coroutine
def get_email(dt_id, cursor):
    query = """select email from dt_user where dt_id=%s"""
    cursor.execute(query, (dt_id,))
    ret = cursor.fetchone()
    raise gen.Return(ret[0])


@gen.coroutine
def is_send_email(dt_id, cursor):
    query = """select count(1) from activated_dt_email_info where dt_id=%s and status=2"""
    cursor.execute(query, (dt_id,))
    ret = cursor.fetchone()
    raise gen.Return(ret[0])


@gen.coroutine
def get_dt_info(dt_id, cursor):
    query = """select
            dt_inlet_info.email,
            dt_inlet_info.dt_name,
            dt_user.dt_id
            from
            dt_user
            inner join dt_inlet_info on dt_inlet_info.dt_id=dt_user.dt_id
            where dt_user.dt_id=%s"""
    cursor.execute(query, (dt_id,))
    ret = cursor.fetchone()
    raise gen.Return(ret)


@gen.coroutine
def main():
    # mch_ids = [100000147767]
    # dt_id = 10000078823
    # dt_ids = [10000005554, 10000006774, 10000063337, 10000050727, 10000037107, 10000045429, 10000056667]
    dt_ids = [10000387291, 10000386597]
    # 开始自动发送邮件
    with db.get_db() as cur:
        for dt_id in dt_ids:
            print dt_id
            yield resend_dt_email(dt_id, cur)


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(main)
