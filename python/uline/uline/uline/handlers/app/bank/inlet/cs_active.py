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

from uline.public.common import gen_randown_mch_pkey
from uline.handlers.baseHandlers import BkAdminHandler
from uline.public import common
from .form import ActivatedMerchantInfo
from uline.public.constants import ACTIVATED_STATUS, PAYMENT
from uline.public import log
from uline.backend import tasks
import tcelery
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()

from uline.settings import MCH_LOGIN_URL, MESSAGE_URL, env


class ActivatedCsInletStatusHandler(BkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = ActivatedMerchantInfo(self)
        self.f_rsp = common.f_rsp(code=406, msg='fail')
        if not form.validate():
            self.finish(self.f_rsp)
        self.mch_id = form.mch_id.data
        self.payment_type = form.pay_type.data
        self.create_at = self.update_at = common.timestamp_now()
        self.activated_status = 2

    @asynchronous
    @gen.coroutine
    def get(self):
        rsp = common.scc_rsp(code=200, msg='success')
        with self.db.get_db() as cur:
            try:
                self.email = yield self.get_email(cur)
                chain_activated_status = yield self.get_chain_activated_status(cur)
                if chain_activated_status in [2, 3]:

                    yield self.activated_cs_payment(cur)
                    yield self.activated_cs_inlet(cur)
                    yield self.add_activated_cs_info(cur)
                    self.mch_info = yield self.get_cs_info(cur)
                else:
                    # 暂时注释激活失败时，把记录写到激活信息表（感觉后期也要加，先留着 (￣Д ￣) ）
                    # yield self.add_activated_mch_info(cur,
                    # activated_status=1)
                    payment_name = PAYMENT[str(self.payment_type)]
                    msg = u'连锁商户{}的费率未激活'.format(payment_name)
                    rsp = common.f_rsp(code=407, msg=msg)
                    self.write(rsp)
                    self.finish()
                    return
            except Exception as err:
                log.exception.info(err)
                cur.connection.rollback()
                rsp = common.f_rsp(code=406, msg='fail')
                self.write(rsp)
                self.finish()
                return

        count = yield self.is_send_email()
        # 如果激活邮件发给渠道商则设置为待发送
        if not count and self.mch_info[4] == 2:
            self.save_activated_cs_email_info('ready', 3)

        if not count and self.mch_info[4] == 1:
            addition_info = u'(浦发银行厦门分行O2O平台合作伙伴)' if env == 'SPD_PROD' else ''
            http_client = AsyncHTTPClient()
            data = {
                'env': env,
                'reciver': self.mch_info[0],
                'title': u'uline连锁门店激活信息',
                'body': u"""
{1}，您好：
以下帐号重要信息请注意保密：
门店编号：{2}
初始密钥：{3}

广州优畅信息技术有限公司{5}
客服电话：4008047555""".format(self.mch_info[0], self.mch_info[1], self.mch_info[2], self.mch_info[3], MCH_LOGIN_URL,
                          addition_info)
            }
            url = MESSAGE_URL + '/v1/email'
            response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
            if response.body == '1':
                self.save_activated_cs_email_info('fail', 1)
            else:
                self.save_activated_cs_email_info('success', 2)

        message_id = gen_randown_mch_pkey(8)
        tasks.callback_for_merchant_active.delay(self.mch_id, message_id)
        self.write(rsp)

    @gen.coroutine
    def get_chain_activated_status(self, cursor):
        query = """SELECT activated_status FROM dt_payment
                    WHERE dt_id=(SELECT cs_id FROM mch_inlet_info WHERE mch_id=%s) and payment_type=%s;"""
        cursor.execute(query, (self.mch_id, self.payment_type))
        ret = cursor.fetchone()
        raise gen.Return(ret[0] if ret else '')

    @gen.coroutine
    def activated_cs_payment(self, cursor):
        query = """update mch_payment set
            activated_status=%(activated_status)s, update_at=%(update_at)s
            where mch_id=%(mch_id)s and payment_type=%(payment_type)s"""
        cursor.execute(query, {
            "activated_status": self.activated_status,
            "mch_id": self.mch_id,
            "update_at": self.update_at,
            "payment_type": self.payment_type
        })

    @gen.coroutine
    def activated_cs_inlet(self, cursor):
        query = """update mch_inlet_info set
            activated_status=%(activated_status)s, update_at=%(update_at)s
            where mch_id=%(mch_id)s"""
        cursor.execute(query, {
            "activated_status": self.activated_status,
            "mch_id": self.mch_id,
            "update_at": self.update_at
        })

    @gen.coroutine
    def add_activated_cs_info(self, cursor, activated_status=None):
        activated_user = yield self.get_bk_email(cursor)
        query = """insert into
            activated_mch_info (mch_id, payment_type, comment, activated_user, activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
        cursor.execute(query, (self.mch_id, self.payment_type,
                               ACTIVATED_STATUS[str(activated_status if activated_status else self.activated_status)
                                                ], activated_user,
                               activated_status if activated_status else self.activated_status,
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
        query = """select count(1) from activated_mch_email_info where mch_id=%s and  (status=2 or status=3)"""
        ret = self.db.selectSQL(query, (self.mch_id,))
        raise gen.Return(ret[0])

    @gen.coroutine
    def get_cs_info(self, cursor):
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
    def save_activated_cs_email_info(self, comment, status):
        query = """insert into
                activated_mch_email_info (mch_id,email,comment,status,create_at)
                values (%s, %s, %s, %s, %s)"""
        self.db.executeSQL(query, (self.mch_id, self.email,
                                   comment, status, self.create_at))
