# -*- coding: utf-8 -*-
from __future__ import division

from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import MchAdminHandler
from .form import MerchantTCapitalInfo
from uline.public.constants import MCH_CLEAR_TYPES
from uline.public.permit import check_permission
from uline.public import common, constants


class MchCapitalInfoHandler(MchAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantTCapitalInfo(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/merchant/capital/')

    def generate_unchanged_render_params(self):
        return {
            "print_money": common.print_money,
            "print_datetime": common.datetime_to_str,
            "clear_action": constants.MCH_CLEAR_ACTIONS,
        }

    @asynchronous
    @gen.coroutine
    def get(self):
        self.mch_id = self.current_user
        self.query_params = {key: getattr(getattr(self.form, key), 'data', None) for key in self.form.data}

        clear_info = self.query_clear_info()
        data = clear_info
        current_balance = 0
        last_balance = 0
        order_result = None
        self.render('merchant/capital/capitalDetail.html', data=data, form=self.form, current_balance=current_balance,
                    last_balance=last_balance, order_result=order_result,
                    print_bussiness_type=self.print_bussiness_type)

    def print_bussiness_type(self, bussiness_type):
        return MCH_CLEAR_TYPES.get(bussiness_type, None) or u'无类型'

    def query_clear_info(self):
        # {'bussiness_type': None, 'cleared': '1', 'business_no': 7667446302864773120, 'channel': 'wx'}
        business_type = self.query_params.get('business_type', None)
        cleared = self.query_params.get("cleared", None)
        business_no = self.query_params.get("business_no", None)
        clear_info = {}
        if cleared:
            clear_info = self.get_mch_clear_info(business_no)
        else:
            method_map = {
                1: self._get_trade_pre_clear_info,
                2: self._get_refund_pre_clear_query,
                3: self._get_withdraw_pre_clear_info,
            }
            method = method_map.get(business_type, None)
            if method:
                query_params = {
                    "mch_id": self.mch_id,
                    "business_no": business_no,
                }
                query = method()
                clear_info = self.db.selectSQL(query, query_params, use_dict=True)
                if clear_info:
                    clear_info = {k: v for k, v in clear_info.items()}
        if clear_info:
            clear_info["cleared"] = cleared
            clear_info["business_type"] = business_type
            order_info = self.get_order_info(business_no, business_type, cleared)
            clear_info.update(order_info)
        if cleared:
            last_balance = self.get_last_balance(self.mch_id, clear_info['create_at'], clear_info['pay_channel'])
            clear_info['last_balance'] = last_balance
        return clear_info

    def get_order_info(self, business_no, bussiness_type, cleared):
        query = None
        if bussiness_type == 1:
            query = """
                select
                wx_transaction_id as transaction_id,mch_trade_no,out_trade_no
                from orders where out_trade_no=%s"""
        elif bussiness_type == 2:
            query = """
                select
                transaction_id,mch_trade_no,out_trade_no,
                refund_id, out_refund_no, mch_refund_no
                from order_refunds where out_refund_no=%s
                """
        order_info = {}
        if query:
            order_info = self.tdb.selectSQL(query, (business_no,), fetchone=True, use_dict=True)
            if order_info:
                order_info = {k: v for k, v in order_info.items()}
        return order_info or {}

    def _get_refund_pre_clear_query(self):
        query = """
                SELECT create_at, 2 AS business_type, out_refund_no AS out_trade_no, mch_id, pay_channel,
                       -refund_fee as trade_amount, mch_profit, (mch_profit-refund_fee) AS real_amount,
                       out_refund_no as business_no
                FROM pre_refund_clear_info
                WHERE mch_id=%(mch_id)s and out_refund_no=%(business_no)s"""
        return query

    def _get_trade_pre_clear_info(self):
        query = """
                SELECT create_at, 1 AS business_type, out_trade_no, mch_id, pay_channel, out_trade_no as business_no,
                       total_fee as trade_amount, mch_profit, (total_fee+mch_profit) AS real_amount
                FROM pre_trade_clear_info
                WHERE mch_id=%(mch_id)s and out_trade_no=%(business_no)s"""
        return query

    def _get_withdraw_pre_clear_info(self):
        query = """
                SELECT create_at, 3 AS business_type, out_trade_no, mch_id, pay_channel, out_trade_no as business_no,
                       -draw_fee as trade_amount, (total_fee - draw_fee), 0-total_fee AS real_amount
                FROM pre_d0_clear_info
                WHERE mch_id=%(mch_id)s and out_trade_no=%(business_no)s"""
        return query

    def get_mch_clear_info(self, business_no):

        mch_id = self.current_user

        query = """
             select
                create_at,
                mch_clear_no,
                business_type,
                trade_amount,
                mch_profit,
                trade_amount + mch_profit as real_amount,
                remarks as remark,
                out_trade_no, current_balance, channel as pay_channel
                from mch_clear_info
                where mch_id=%(mch_id)s
                and (mch_clear_no::VARCHAR = %(mch_clear_no)s::VARCHAR)
        """

        # 支付宝和微信的余额不一样
        data = self.db.selectSQL(query, {
            'mch_id': str(mch_id),
            'mch_clear_no': business_no,
        }, fetchone=True, use_dict=True)

        clear_info = {k: v for k, v in data.items()}

        return clear_info

    # 获取变更前的金额
    def get_last_balance(self, mch_id, create_at, channel):
        sql = """select current_balance, mch_clear_no from mch_clear_info
                 where create_at<%(create_at)s and mch_id=%(mch_id)s and channel=%(channel)s
                 order by create_at desc limit 1"""
        # 支付宝和微信的余额不一样
        data = self.db.selectSQL(sql, {'mch_id': str(mch_id), 'create_at': create_at, 'channel': channel},
                                 fetchone=True, use_dict=True)
        last_balance = data[0] if data and data[0] else 0
        return last_balance
