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
from .form import ActivatedBatchMerchantInfo
from uline.public.constants import ACTIVATED_STATUS, PAYMENT
from uline.public import log
from uline.backend import tasks
from uline.settings import env, MCH_LOGIN_URL, MESSAGE_URL
from uline.public.common import gen_randown_mch_pkey
import tcelery
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()


class ActivatedBatchMerchantInletStatusHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = ActivatedBatchMerchantInfo(self)
        self.f_rsp = common.f_rsp(code=406, msg='fail')

        if not form.validate():
            self.finish(self.f_rsp)
        self.mch_id = form.mch_id.data
        self.create_at = self.update_at = common.timestamp_now()
        self.activated_status = 2

    @asynchronous
    @gen.coroutine
    def get(self):
        rsp = common.scc_rsp(code=200, msg='success')
        with self.db.get_db() as cur:
            try:
                payment_types = yield self.get_unactivated_payment_type(cur)
                dt_unactivated_payment_type = yield self.get_dt_unactivated_payment_type(cur)
                if dt_unactivated_payment_type:
                    payment_name = '、'.join(PAYMENT[str(payment_type[0])]
                                            for payment_type in dt_unactivated_payment_type if payment_type in payment_types)
                    if payment_name:
                        msg = u'渠道商{}的费率未激活'.format(payment_name)
                        rsp = common.f_rsp(code=407, msg=msg)
                        self.write(rsp)
                        self.finish()
                        return
                self.email = yield self.get_email(cur)
                yield self.activated_mch_payment(cur)
                yield self.activated_mch_inlet(cur)
                yield self.add_activated_mch_info(cur, payment_types)
                self.mch_info = yield self.get_mch_info(cur)
            except Exception as err:
                log.exception.info(err)
                cur.connection.rollback()
                rsp = common.f_rsp(code=406, msg='fail')
                self.write(rsp)
                self.finish()
                return

        count = yield self.is_send_email()
        if not count and self.mch_info[4] == 2:
            self.save_activated_mch_email_info('ready', 3)

        if not count and self.mch_info[4] == 1:
            addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': self.mch_info[0],
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
客服电话：4008047555""".format(str(self.mch_info[2]) + ".mch", self.mch_info[1], self.mch_info[2], self.mch_info[3], MCH_LOGIN_URL,
                          addition_info)
            }
            url = MESSAGE_URL + '/v1/email'
            print url
            response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
            if response.body == '1':
                self.save_activated_mch_email_info('fail', 1)
            else:
                self.save_activated_mch_email_info('success', 2)

        message_id = gen_randown_mch_pkey(8)
        tasks.callback_for_merchant_active.delay(self.mch_id, message_id)
        self.write(rsp)

    @gen.coroutine
    def get_unactivated_payment_type(self, cursor):
        query = """select payment_type from mch_payment where mch_id=%(mch_id)s and activated_status=1;"""
        cursor.execute(query, {"mch_id": self.mch_id})
        ret = cursor.fetchall()
        raise gen.Return(ret)

    @gen.coroutine
    def get_dt_unactivated_payment_type(self, cursor):
        query = """SELECT payment_type FROM dt_payment
                    WHERE dt_id=(SELECT dt_id FROM mch_inlet_info
                    WHERE mch_id=%s) and activated_status=1;"""
        cursor.execute(query, (self.mch_id, ))
        ret = cursor.fetchall()
        raise gen.Return(ret if ret else '')

    @gen.coroutine
    def activated_mch_payment(self, cursor):
        query = """update mch_payment set
            activated_status=%(activated_status)s, update_at=%(update_at)s
            where mch_id=%(mch_id)s and activated_status=1"""
        cursor.execute(query, {
            "activated_status": self.activated_status,
            "mch_id": self.mch_id,
            "update_at": self.update_at
        })

    @gen.coroutine
    def activated_mch_inlet(self, cursor):
        query = """update mch_inlet_info set
            activated_status=%(activated_status)s, update_at=%(update_at)s
            where mch_id=%(mch_id)s"""
        cursor.execute(query, {
            "activated_status": self.activated_status,
            "mch_id": self.mch_id,
            "update_at": self.update_at
        })

    @gen.coroutine
    def add_activated_mch_info(self, cursor, payment_types):
        activated_user = yield self.get_bk_email(cursor)
        for _, payment_type in enumerate(payment_types):
            query = """insert into
                activated_mch_info (mch_id, payment_type, comment, activated_user, activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
            cursor.execute(query, (self.mch_id, payment_type,
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
        query = """select email from mch_user where mch_id=%s"""
        cursor.execute(query, (self.mch_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    @gen.coroutine
    def is_send_email(self):
        query = """select count(1) from activated_mch_email_info where mch_id=%s and status=2"""
        ret = self.db.selectSQL(query, (self.mch_id,))
        raise gen.Return(ret[0])

    @gen.coroutine
    def get_mch_info(self, cursor):
        query = """select
                mch_inlet_info.email,
                mch_inlet_info.mch_name,
                mch_user.mch_id,
                mch_user.mch_pay_key,
                mch_inlet_info.activate_email_tag
                from
                mch_user
                inner join mch_inlet_info on mch_inlet_info.mch_id=mch_user.mch_id
                where mch_user.mch_id=%s"""
        cursor.execute(query, (self.mch_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def save_activated_mch_email_info(self, comment, status):
        query = """insert into
                activated_mch_email_info (mch_id,email,comment,status,create_at)
                values (%s, %s, %s, %s, %s)"""
        self.db.executeSQL(query, (self.mch_id, self.email, comment, status, self.create_at))
