# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from .form import MerchantTradeList
from uline.public.constants import WX_TRADE_STATE, WX_TRADE_TYPE
from uline.public.permit import check_permission


class MerchantsTransactionTradeListHandler(BkAdminHandler):
    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = MerchantTradeList(self)
        if not form.validate():
            self.redirect('/bank/transaction/trade')
            return
        self.wx_transaction_id = form.wx_transaction_id.data

        self.cs_id = None if self.get_argument(
            'cs_id') == "None" else self.get_argument('cs_id')
        self.cs_dt = self.get_cs_dt_name(
            int(self.cs_id)) if self.cs_id else None

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = self.do_execute()
        cs = {"cs_id": self.cs_id, "cs_dt_name": self.cs_dt[0], "cs_dt_shortname": self.cs_dt[1]} if self.cs_id else {
            "cs_id": self.cs_id}
        data.update(cs)
        self.render('bank/transaction/merchantTradeList.html', data=data)

    def do_execute(self):
        tb_query = """select
                ul_mch_id,
                to_char(created_at, 'YYYY-MM-DD HH24:MI:SS'),
                out_trade_no,
                wx_transaction_id,
                mch_trade_no,
                trade_state,
                trade_type,
                total_fee,
                detail,
                to_char(complete_at, 'YYYY-MM-DD HH24:MI:SS')
                from orders
                where wx_transaction_id=%s;"""
        tb_ret = self.tdb.selectSQL(tb_query, (self.wx_transaction_id,))
        tb_ret = self.deal_data(tb_ret) if tb_ret else []
        tb_fields = ['mch_id', 'created_at', 'out_trade_no', 'wx_transaction_id',
                     'mch_trade_no', 'trade_state', 'trade_type', 'total_fee', 'detail', 'complete_at']
        tb_ret_d = dict(zip(tb_fields, tb_ret))

        ul_query = """select mch_user.mch_name,mch_inlet_info.mch_shortname,
                       dt_user.dt_name,bk_user.bk_id,bk_user.bk_name,
                       bk_user.bk_type
                       from mch_user
                       inner join mch_inlet_info on mch_inlet_info.mch_id = mch_user.mch_id
                       inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
                       inner join bk_user on bk_user.bk_id = mch_inlet_info.bk_id
                       where mch_user.mch_id=%s;"""
        ul_ret = self.db.selectSQL(ul_query, (tb_ret[0],))
        ul_fields = ['mch_name', 'mch_shortname', 'dt_name', 'bk_id', 'bk_name', 'bk_type']
        ul_ret_d = dict(zip(ul_fields, ul_ret))

        tb_ret_d.update(ul_ret_d)
        return tb_ret_d

    def deal_data(self, data):
        _d = list(data)
        _d[5], _d[6], _d[7] = WX_TRADE_STATE[_d[5]
                                             ], WX_TRADE_TYPE[_d[6]], _d[7] / 100
        return _d

    def get_cs_dt_name(self, cs_id):
        query = """select dt_name, dt_short_name from dt_inlet_info where dt_id =%(dt_id)s;"""
        ret = self.db.selectSQL(query, {'dt_id': cs_id})
        return ret