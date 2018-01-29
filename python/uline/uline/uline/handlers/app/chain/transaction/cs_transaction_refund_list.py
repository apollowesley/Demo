# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import MerchantRefundList
from uline.public.constants import WX_REFUND_STATE, WX_TRADE_TYPE
from uline.public.permit import check_permission


class CsTransactionRefundListHandler(ChainAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = MerchantRefundList(self)
        if not form.validate():
            self.redirect('/chain/transaction/refund')
            return
        self.out_refund_no = form.out_refund_no.data

    def get(self):
        data = self.do_execute()
        self.render('chain/transaction/csRefundList.html', data=data)

    def do_execute(self):
        tb_query = """select
                  order_refunds.ul_mch_id,
                  order_refunds.out_trade_no,
                  order_refunds.out_refund_no,
                  order_refunds.mch_trade_no,
                  order_refunds.mch_refund_no,
                  order_refunds.transaction_id,
                  order_refunds.refund_id,
                  orders.total_fee,
                  order_refunds.refund_fee,
                  orders.trade_type,
                  order_refunds.refund_channel,
                  order_refunds.checked_flag,
                  order_refunds.refund_status,
                  to_char(order_refunds.created_at, 'YYYY-MM-DD HH24:MI:SS'),
                  orders.sub_mch_id
                   from
                   order_refunds
                   inner join orders on order_refunds.out_trade_no = orders.out_trade_no
                   where order_refunds.out_refund_no=%(out_refund_no)s"""
        tb_ret = self.tdb.selectSQL(
            tb_query, {'out_refund_no': self.out_refund_no})
        tb_ret = self.deal_data(tb_ret)

        ul_mch_id = tb_ret[0] if tb_ret else 0
        ul_query = """select
                       mch_user.mch_name,
                       mch_inlet_info.mch_shortname,
                       dt_user.dt_name,
                       dt_user.dt_id
                       from mch_user
                       inner join mch_inlet_info on mch_inlet_info.mch_id = mch_user.mch_id
                       inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
                       where mch_user.mch_id=%s and mch_inlet_info.cs_id is not null;"""
        ul_ret = self.db.selectSQL(ul_query, (ul_mch_id, ))

        tb_fields = ['mch_id', 'out_trade_no', 'out_refund_no', 'mch_trade_no', 'mch_refund_no',
                     'transaction_id', 'refund_id', 'total_fee', 'refund_fee', 'trade_type', 'refund_channel',
                     'checked_flag', 'refund_status', 'created_at', 'sub_mch_id']
        ul_fields = ['mch_name', 'mch_shortname', 'dt_name', 'dt_id']

        ret = dict(zip(tb_fields, tb_ret))
        ul_ret_d = dict(zip(ul_fields, ul_ret))

        ret.update(ul_ret_d)
        return ret

    def deal_data(self, data):
        _d = list(data)
        _d[7], _d[8], _d[9], _d[12] = _d[7] / 100, _d[8] / \
            100, WX_TRADE_TYPE[_d[9]], WX_REFUND_STATE[_d[12]]
        return _d
