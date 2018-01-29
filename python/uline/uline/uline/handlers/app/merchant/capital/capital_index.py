# -*- coding: utf-8 -*-
from __future__ import division
from datetime import timedelta

from tornado import gen
from tornado.web import authenticated, asynchronous

from .form import MerchantTCapitalSearch
from uline.public.permit import check_permission
from uline.public import common
from uline.public import constants
from uline.handlers.baseHandlers import MchAdminHandler


class MchCapitalIndexHandler(MchAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantTCapitalSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/merchant/')
            return
        self.pageindex = int(self.get_argument("p", 1))
        self.render_url = 'merchant/capital/capital.html'
        self.mch_id = self.current_user
        # if self.form.channel.data == "alipay":
        # self.render_url = 'merchant/capital/capital_ali.html'

    def get(self):
        cleared = self.form.cleared.data or 0
        business_type = self.form.business_type.data or 0
        if business_type > 3 and not cleared:
            ret = [[], 0, 0]
        elif cleared:
            ret = self.db_execute(self.form, (self.pageindex - 1) * 10)
        else:
            ret = self.db_execute_cleared(self.form, (self.pageindex - 1) * 10)
        data, total_number, balance = ret[0], ret[1], ret[2]
        query_info = {k: v for k, v in self.form.data.iteritems() if v}
        navigate_html = self.get_navigate_html(total_number, **query_info)
        self.render(
            self.render_url,
            navigate_html=navigate_html, data=data,
            total_number=total_number, balance=balance,
            form=self.form, cleared=cleared
        )

    def generate_unchanged_render_params(self):
        return {
            "print_money": common.print_money,
            "print_datetime": common.datetime_to_str,
            "clear_action": constants.MCH_CLEAR_ACTIONS,
        }

    @asynchronous
    @gen.coroutine
    def post(self):
        self.get()

    def db_execute(self, form, offset):
        business_type = form.business_type.data or None
        mch_clear_no = form.mch_clear_no.data or None
        out_trade_no = form.out_trade_no.data or None
        channel = form.channel.data or None
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None

        ret, total = [], 0
        mch_id = self.current_user

        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """
            select
                create_at,
                business_type,
                mch_clear_no,
                payment_type,
                out_trade_no,
                current_balance,
                trade_amount,
                mch_profit,
                trade_amount + mch_profit as real_amount,
                mch_clear_no as jump_no, channel as pay_channel,
                COUNT(*) OVER () AS total
            from mch_clear_info
            where mch_id=%(mch_id)s
                and (business_type=%(business_type)s or %(business_type)s is null)
                and (mch_clear_no::VARCHAR ~ %(mch_clear_no)s::VARCHAR or %(mch_clear_no)s::VARCHAR is null)
                and (out_trade_no::VARCHAR ~ %(out_trade_no)s::VARCHAR or %(out_trade_no)s::VARCHAR is null)
                and channel=%(channel)s
                and (create_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                or %(create_at_start)s is null or %(create_at_end)s is null)
            order by create_at desc
            offset %(offset)s rows fetch next 10 rows only;
        """
        if channel == 'wx':
            channel = "weixin"

        data = self.db.selectSQL(query, {
            'channel': channel,
            'mch_id': str(mch_id),
            'business_type': business_type,
            'mch_clear_no': mch_clear_no, 'out_trade_no': out_trade_no,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'offset': offset}, fetchone=False, use_dict=True)  # 每页显示10条数据

        data = [{k: v for k, v in info.items()} for info in data]
        for index, each_data in enumerate(data):
            if each_data['trade_amount'] is None or each_data['current_balance'] is None:
                del data[index]

        if data:
            ret, total = data, data[0]["total"]  # 数据,总数

        current_balance = self.get_current_balance(channel)

        return ret, total, current_balance

    def db_execute_cleared(self, form, offset):
        business_type = form.business_type.data or None
        mch_clear_no = form.mch_clear_no.data or None
        out_trade_no = form.out_trade_no.data or None
        channel = form.channel.data or None
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None

        mch_id = self.current_user

        if channel == 'alipay':
            pay_channel = 'alipay'
        else:
            pay_channel = 'weixin'

        last_settle_time_query = """select max(create_at) from mch_clear_info;"""
        last_settle_time = self.db.selectSQL(last_settle_time_query, fetchone=True)
        if last_settle_time:
            last_settle_time = last_settle_time[0]

        order_clear_query = """
                SELECT create_at, 1 AS business_type, out_trade_no, mch_id, pay_channel,
                       total_fee as trade_amount, mch_profit, (total_fee+mch_profit) AS real_amount,
                       out_trade_no as jump_no
                FROM pre_trade_clear_info
                WHERE mch_id=%(mch_id)s and
                     complete_at>=%(last_settle_time)s and
                     (pay_channel=%(pay_channel)s or %(pay_channel)s is null)"""
        refund_clear_query = """
                SELECT create_at, 2 AS business_type, out_refund_no AS out_trade_no, mch_id, pay_channel,
                       -refund_fee as trade_amount, mch_profit,  (mch_profit-refund_fee) AS real_amount,
                       out_refund_no as jump_no
                FROM pre_refund_clear_info
                WHERE mch_id=%(mch_id)s and
                     complete_at>=%(last_settle_time)s and
                     (pay_channel=%(pay_channel)s or %(pay_channel)s is null)"""

        withdraw_clear_query = """
                SELECT create_at, 3 AS business_type, out_trade_no, mch_id, pay_channel,
                       -draw_fee as trade_amount, (total_fee - draw_fee) as mch_profit, 0-total_fee AS real_amount,
                        out_trade_no as jump_no
                FROM pre_d0_clear_info
                WHERE mch_id=%(mch_id)s and
                     complete_at>=%(last_settle_time)s and
                     (pay_channel=%(pay_channel)s or %(pay_channel)s is null)"""

        querys = [order_clear_query, refund_clear_query, withdraw_clear_query]
        if not business_type:
            sub_query = "\n UNION ALL \n".join(querys)
        else:
            sub_query = querys[business_type - 1]
        where_clause = """
            mch_id=%(mch_id)s
            and (business_type=%(business_type)s or %(business_type)s is null)
            and (out_trade_no::VARCHAR ~ %(out_trade_no)s::VARCHAR or %(out_trade_no)s::VARCHAR is null)
            and (pay_channel=%(pay_channel)s or %(pay_channel)s is null)
            and (create_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
            or %(create_at_start)s is null or %(create_at_end)s is null)
        """
        query_params = {
            'mch_id': mch_id,
            'business_type': business_type,
            'mch_clear_no': mch_clear_no,
            'out_trade_no': out_trade_no,
            'pay_channel': pay_channel,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'last_settle_time': last_settle_time,
            'offset': offset
        }
        all_amount_query = """select count(*) from ({}) as clear_infos where {}""".format(sub_query, where_clause)
        total = self.db.selectSQL(all_amount_query, query_params, fetchone=True, use_dict=True)
        total = total[0]

        offset_clause = """ order by create_at desc offset %(offset)s rows fetch next 10 rows only;"""
        where_clause += offset_clause
        query = """select * from ({}) as clear_infos where {}""".format(sub_query, where_clause)
        data = self.db.selectSQL(query, query_params, fetchone=False, use_dict=True)  # 每页显示10条数据
        # end

        current_balance = self.get_current_balance(pay_channel)
        data = [{k: v for k, v in info.items()} for info in data]
        return data, total, current_balance

    def get_current_balance(self, pay_channel):
        balance_sql = """
            SELECT
              mch_id,
              pay_channel,
              sum(profit_total)
            FROM mch_book
            WHERE
              mch_id = %(mch_id)s AND
              pay_channel = %(pay_channel)s AND
              status!=%(status)s
              GROUP BY mch_id, pay_channel;
        """

        params = {
            'mch_id': self.mch_id,
            'status': 1,
            'pay_channel': pay_channel
        }
        row = self.db.selectSQL(balance_sql, params, use_dict=True)
        if row:
            current_balance = float(row.get('sum'))
        else:
            current_balance = 0
        return current_balance
