# -*- coding: utf-8 -*-
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import MchAdminHandler
from .form import MerchanCanRefund
from uline.public import common
from uline.public.permit import check_permission


class MerchantsTransactionCanRefundHandler(MchAdminHandler):

    @authenticated
    @check_permission("/transaction/trade")
    def prepare(self):
        form = MerchanCanRefund(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.out_trade_no = form.out_trade_no.data
        self.mch_id = self.current_user

    @asynchronous
    @gen.coroutine
    def get(self):
        can_refund = yield self.do_execute()
        if not can_refund:
            s_rsp = common.scc_rsp(code=406, msg='Refund amount is less than 0')
            self.write(s_rsp)
        else:
            has_refund_password = yield self.has_refund_password_or_not()
            if has_refund_password:
                s_rsp = common.scc_rsp(code=200, msg='success')
            else:
                s_rsp = common.scc_rsp(code=405, msg='Please set up a refund password')
            self.write(s_rsp)

    @gen.coroutine
    def do_execute(self):
        can_refund = True
        # 先查询该订单的退款总金额，算出可退金额
        refund_fee_query = """SELECT sum(refund_fee)
                  from order_refunds WHERE out_trade_no=%(out_trade_no)s"""
        refund_ret = self.tdb.selectSQL(refund_fee_query, {'out_trade_no': self.out_trade_no})

        if refund_ret and refund_ret[0]:
            total_fee_query = """SELECT total_fee from orders WHERE out_trade_no=%(out_trade_no)s"""
            total_fee_query = self.tdb.selectSQL(total_fee_query, {'out_trade_no': self.out_trade_no})
            can_refund_fee = total_fee_query[0] - refund_ret[0]
            if can_refund_fee <= 0:
                can_refund = False

        raise gen.Return(can_refund)

    @gen.coroutine
    def has_refund_password_or_not(self):
        has_refund_query = """select refund_password from mch_user where mch_id=%(mch_id)s"""
        ret = self.db.selectSQL(has_refund_query, {'mch_id': self.mch_id})
        data = True if ret and ret[0] else False
        raise gen.Return(data)
