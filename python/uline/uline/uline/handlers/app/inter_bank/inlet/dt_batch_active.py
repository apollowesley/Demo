# -*- coding: utf-8 -*-
'''
BEGIN
ajax请求 激活商户支付方式和状态
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import json

from tornado.httpclient import AsyncHTTPClient
from tornado.web import asynchronous, authenticated
from tornado import gen
from uline.handlers.baseHandlers import IntBkAdminHandler
from uline.public import common
from form import ActivatedBatchDistributorInfo
from uline.public import log
from uline.public.constants import ACTIVATED_STATUS
from uline.settings import env, MESSAGE_URL
import tcelery
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()

from uline.settings import DIST_LOGIN_URL


class ActivatedBatchDistributorInletStatusHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = ActivatedBatchDistributorInfo(self)
        self.f_rsp = common.f_rsp(code=406, msg='fail')

        if not form.validate():
            self.finish(self.f_rsp)
        self.dt_id = form.dt_id.data
        self.create_at = self.update_at = common.timestamp_now()
        self.activated_status = 2

    @asynchronous
    @gen.coroutine
    def get(self):
        self.rsp = common.scc_rsp(code=200, msg='success')

        with self.db.get_db() as cur:
            try:
                payment_types = yield self.get_unactivated_payment_type(cur)
                self.email = yield self.get_email(cur)
                yield self.activated_dt_payment(cur)
                yield self.activated_dt_inlet(cur)
                yield self.add_activated_dt_info(cur, payment_types)
                self.dt_info = yield self.get_dt_info(cur)
            except Exception as err:
                log.exception.info(err)
                cur.connection.rollback()
                self.rsp = common.f_rsp(code=406, msg='fail')

        count = yield self.is_send_email()
        if not count:
            addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': self.dt_info[0],
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
客服电话：4008047555""".format(str(self.dt_info[2]) + ".dt", self.dt_info[1], self.dt_info[2], DIST_LOGIN_URL, addition_info)
            }
            url = MESSAGE_URL + '/v1/email'
            response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
            if response.body == '1':
                self.save_activated_dt_email_info('fail', 1)
            else:
                self.save_activated_dt_email_info('success', 2)
        self.write(self.rsp)

    @gen.coroutine
    def get_unactivated_payment_type(self, cursor):
        query = """select payment_type from dt_payment where dt_id=%(dt_id)s and activated_status=1;"""
        cursor.execute(query, {"dt_id": self.dt_id})
        ret = cursor.fetchall()
        raise gen.Return(ret)

    @gen.coroutine
    def activated_dt_payment(self, cursor):
        query = """update dt_payment set
            activated_status=%(activated_status)s, update_at=%(update_at)s
            where dt_id=%(dt_id)s and activated_status=1;"""
        cursor.execute(query, {
            "activated_status": self.activated_status,
            "dt_id": self.dt_id,
            "update_at": self.update_at
        })

    @gen.coroutine
    def activated_dt_inlet(self, cursor):
        query = """update dt_inlet_info set
            activated_status=%(activated_status)s, update_at=%(update_at)s
            where dt_id=%(dt_id)s"""
        cursor.execute(query, {
            "activated_status": self.activated_status,
            "dt_id": self.dt_id,
            "update_at": self.update_at
        })

    @gen.coroutine
    def add_activated_dt_info(self, cursor, payment_types):
        activated_user = yield self.get_bk_email(cursor)
        for _, payment_type in enumerate(payment_types):
            query = """insert into
                activated_dt_info (dt_id, payment_type, comment, activated_user, activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
            cursor.execute(query, (self.dt_id, payment_type,
                                   ACTIVATED_STATUS[str(self.activated_status)
                                                    ], activated_user, self.activated_status,
                                   self.create_at))

    @gen.coroutine
    def get_bk_email(self, cursor):
        query = """select email from bk_user where bk_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    @gen.coroutine
    def get_email(self, cursor):
        query = """select email from dt_user where dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    @gen.coroutine
    def is_send_email(self):
        query = """select count(1) from activated_dt_email_info where dt_id=%s and status=2"""
        ret = self.db.selectSQL(query, (self.dt_id,))
        raise gen.Return(ret[0])

    @gen.coroutine
    def get_dt_info(self, cursor):
        query = """select
                dt_inlet_info.email,
                dt_inlet_info.dt_name,
                dt_user.dt_id
                from
                dt_user
                inner join dt_inlet_info on dt_inlet_info.dt_id=dt_user.dt_id
                where dt_user.dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def save_activated_dt_email_info(self, comment, status):
        query = """insert into
                activated_dt_email_info (dt_id,email,comment,status,create_at)
                values (%s, %s, %s, %s, %s)"""
        self.db.executeSQL(query, (self.dt_id, self.email, comment, status, self.create_at))
