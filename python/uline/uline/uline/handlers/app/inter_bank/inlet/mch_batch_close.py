# -*- coding: utf-8 -*-
'''
BEGIN
ajax请求 关闭商户 所有支付类型
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
from tornado import gen
from tornado.web import asynchronous, authenticated
from uline.handlers.baseHandlers import IntBkAdminHandler
from uline.public import common, log
from .form import CloseBatchMerchantPayment
from uline.backend import tasks
from uline.public.permit import check_permission


class CloseBatchMerchantPaymentHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = CloseBatchMerchantPayment(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.mch_id = form.mch_id.data
        self.update_at = common.timestamp_now()

    # 关闭商户 所有支付类型
    @asynchronous
    @gen.coroutine
    def post(self):
        rsp = common.scc_rsp(code=200, msg='success')
        with self.db.get_db() as cur:
            try:
                payment_types = self.get_activated_payment_type(cur)
                # 关闭商户
                self.close_mch_payment(cur)
                # 添加关闭记录到 商户激活记录信息表
                self.add_record(cur, payment_types)
                self.update_mch_id_activate_status(cur)

                message_id = common.gen_randown_mch_pkey(8)
                tasks.callback_for_merchant_active.delay(self.mch_id, message_id)

            except Exception as err:
                log.exception.info(err)
                cur.connection.rollback()
                rsp = common.f_rsp(code=406, msg='fail')
        self.write(rsp)
        self.finish()
        return

    def get_activated_payment_type(self, cursor):
        query = """select payment_type from mch_payment where mch_id=%(mch_id)s and activated_status=2;"""
        cursor.execute(query, {"mch_id": self.mch_id})
        ret = cursor.fetchall()
        return ret

    def close_mch_payment(self, cursor):
        query = """update mch_payment set activated_status=1, update_at=%(update_at)s
                    where mch_id=%(mch_id)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'mch_id': self.mch_id,
        })

    def update_mch_id_activate_status(self, cursor):
        query = """update mch_inlet_info set activated_status=1, update_at=%(update_at)s
                    WHERE mch_id=%(mch_id)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'mch_id': self.mch_id
        })

    def add_record(self, cursor, payment_types):
        activated_user = self.get_bk_email(cursor)
        for _, payment_type in enumerate(payment_types):
            query = """insert into
                        activated_mch_info (mch_id, payment_type, comment, activated_user,
                        activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
            cursor.execute(query, (self.mch_id, payment_type,
                                   '已关闭', activated_user, 1,
                                   self.update_at))

    def get_bk_email(self, cursor):
        query = """select email from bk_user where bk_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0]
