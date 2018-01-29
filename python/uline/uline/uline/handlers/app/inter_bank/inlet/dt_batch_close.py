# -*- coding: utf-8 -*-
'''
BEGIN
ajax请求 关闭渠道商 某一个支付类型
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
from .form import CloseBatchDistributorPayment
from uline.backend import tasks
from uline.public.permit import check_permission


class CloseBatchDistributorPaymentHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        form = CloseBatchDistributorPayment(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.dt_id = form.dt_id.data
        self.update_at = common.timestamp_now()

    # 关闭渠道商 所有支付类型
    @asynchronous
    @gen.coroutine
    def post(self):
        rsp = common.scc_rsp(code=200, msg='success')
        with self.db.get_db() as cur:
            try:
                payment_types = self.get_activated_payment_type(cur)
                # 关闭渠道商
                self.close_dt_paymnet(cur)

                self.add_record(cur, payment_types)
                self.update_dt_activate_status(cur)

                # 查询该渠道商下所有商户，包括连锁门店
                mch_ids = self.get_mch_ids_by_dt_id(cur)
                # 关闭商户
                if mch_ids:
                    self.close_mch_payment(cur, mch_ids)
                for mch_id in mch_ids:
                    # 查看该商户是否关闭了所有支付类型
                    ret = self.mch_is_all_close(cur, mch_id)
                    if not ret:
                        self.update_mch_activate_status(cur, mch_id)

                # 关闭连锁商户
                chain_ids = self.get_chain_ids_by_parent_id(cur)
                if chain_ids:
                    self.close_chain_payment(cur, chain_ids)

                for chain_id in chain_ids:
                    ret = self.chain_is_all_close(cur, chain_id)
                    if ret:
                        self.update_chain_activate_status(cur, chain_id)

            except Exception as err:
                log.exception.info(err)
                cur.connection.rollback()
                rsp = common.f_rsp(code=406, msg='fail')
                self.write(rsp)
                self.finish()
                return

        for mch_id in mch_ids:
            message_id = common.gen_randown_mch_pkey(8)
            tasks.callback_for_merchant_active.delay(str(mch_id[0]), message_id)

        self.write(rsp)
        self.finish()
        return

    def mch_is_all_close(self, cursor, mch_id):
        query = """select 1 FROM mch_payment WHERE mch_id=%(mch_id)s and activated_status=2"""
        cursor.execute(query, {
            'mch_id': mch_id,
        })
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def update_mch_activate_status(self, cursor, mch_id):
        query = """update mch_inlet_info set activated_status=1, update_at=%(update_at)s
                    WHERE mch_id=%(mch_id)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'mch_id': mch_id
        })

    def get_mch_ids_by_dt_id(self, cursor):
        query = """select DISTINCT(mch_id) FROM mch_inlet_info WHERE dt_id=%(dt_id)s;"""
        cursor.execute(query, {
            'dt_id': self.dt_id,
        })
        ret = cursor.fetchall()
        return ret

    def get_activated_payment_type(self, cursor):
        query = """select payment_type from dt_payment where dt_id=%(dt_id)s and activated_status=2;"""
        cursor.execute(query, {"dt_id": self.dt_id})
        ret = cursor.fetchall()
        return ret

    def close_dt_paymnet(self, cursor):
        query = """update dt_payment set activated_status=1, update_at=%(update_at)s
                    where dt_id=%(dt_id)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'dt_id': self.dt_id
        })

    def update_dt_activate_status(self, cursor):
        query = """update dt_inlet_info set activated_status=1, update_at=%(update_at)s
                    WHERE dt_id=%(dt_id)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'dt_id': self.dt_id
        })

    def close_mch_payment(self, cursor, mch_ids):
        mch_ids = tuple([mch_id[0] for mch_id in mch_ids])
        query = """update mch_payment set activated_status=1, update_at=%(update_at)s
                    WHERE mch_payment.mch_id IN %(mch_ids)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'dt_id': self.dt_id,
            'mch_ids': mch_ids
        })

    def add_record(self, cursor, payment_types):
        activated_user = self.get_bk_email(cursor)
        for _, payment_type in enumerate(payment_types):
            query = """insert into
              activated_dt_info (dt_id, payment_type, comment, activated_user,
                                 activated_status, create_at) values(%s, %s,%s, %s, %s, %s)"""
            cursor.execute(query, (self.dt_id, payment_type,
                                   '已关闭', activated_user, 1,
                                   self.update_at))

    def get_bk_email(self, cursor):
        query = """select email from bk_user where bk_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0]

    def get_chain_ids_by_parent_id(self, cursor):
        query = """select dt_inlet_info.dt_id FROM dt_inlet_info WHERE dt_inlet_info.parent_id=%(dt_id)s;"""
        cursor.execute(query, {'dt_id': self.dt_id})
        ret = cursor.fetchall()
        return ret

    def close_chain_payment(self, cursor, chain_ids):
        chain_ids = tuple([chain_id[0] for chain_id in chain_ids])
        query = """update dt_payment set activated_status=1, update_at=%(update_at)s
                    WHERE dt_payment.dt_id IN %(dt_ids)s"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'dt_ids': chain_ids
        })

    def chain_is_all_close(self, cursor, chain_id):
        query = """select 1 FROM dt_payment WHERE dt_id=%(dt_id)s and activated_status=2"""
        cursor.execute(query, {
            'dt_id': chain_id,
        })
        ret = cursor.fetchone()
        return False if ret else True

    def update_chain_activate_status(self, cursor, chain_id):
        query = """update dt_inlet_info set activated_status=1, update_at=%(update_at)s WHERE dt_id=%(dt_id)s;"""
        cursor.execute(query, {
            'update_at': self.update_at,
            'dt_id': chain_id
        })
