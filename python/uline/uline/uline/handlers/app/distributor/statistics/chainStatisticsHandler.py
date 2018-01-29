# -*- coding: utf-8 -*-
from __future__ import division
from tornado import gen
from tornado.web import asynchronous, authenticated
from concurrent.futures import ThreadPoolExecutor
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import log, common
from .form import ChainStatisticsSearch
from datetime import timedelta
from uline.public.permit import check_permission


class ChainStatisticsHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = ChainStatisticsSearch(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
            return
        self.pageindex = int(self.get_argument("p", 1))
        if not self.form.create_at_start.data:
            # 默认查询昨天的交易数据
            self.form.create_at_start.data = \
                (common.timestamp_now().replace(
                    hour=0, minute=0, second=0) - timedelta(days=1)).date()
        if not self.form.order_by.data:
            self.form.order_by.data = 'day_tx_count'

    @asynchronous
    @gen.coroutine
    def get(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number = ret[0], ret[1]
        navigate_html = self.get_navigate_html(total_number)
        self.render('distributor/statistics/chainStatistics.html', navigate_html=navigate_html, data=data, form=self.form,
                    total_num=total_number)

    @asynchronous
    @gen.coroutine
    def post(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number = ret[0], ret[1]
        navigate_html = self.get_navigate_html(total_number)
        self.render('distributor/statistics/chainStatistics.html', navigate_html=navigate_html, data=data, form=self.form,
                    total_num=total_number)

    @gen.coroutine
    def db_execute(self, form, offset):
        create_at_start = form.create_at_start.data + timedelta(days=1)
        create_at_end = form.create_at_start.data + timedelta(days=2)
        dt_id = self.get_current_user()

        order_by = form.order_by.data

        chain_name = form.chain_name.data or None
        chain_id = form.chain_id.data or None
        ret, total = [], 0

        _query = """SELECT dt_inlet_info.dt_name, dt_inlet_info.dt_id,
                    sum(ci.day_tx_count) as day_tx_count,
                    round(sum(ci.day_tx_amount)/100, 2) as day_tx_amount,
                    sum(ci.day_refund_count) as day_refund_count,
                    abs(round(sum(ci.day_refund_amount)/100, 2)) as day_refund_amount,
                    round(sum(ci.day_tx_net_amout)/100, 2) as day_tx_net_amout,
                    abs(round(sum(ci.day_profit_amount)/100, 2)) as day_profit_amount,
                 COUNT(*) OVER () AS total
                 FROM cs_daily_balance_info as ci
                 LEFT JOIN dt_inlet_info on ci.cs_id = dt_inlet_info.dt_id
                 INNER JOIN dt_user on dt_user.dt_id = dt_inlet_info.parent_id
                 WHERE (ci.need_pay_time between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp)
                 AND (dt_inlet_info.dt_name ~ E%(chain_name)s or %(chain_name)s = '')
                 AND (dt_inlet_info.dt_id::VARCHAR ~ E%(chain_id)s or %(chain_id)s = '')
                 AND (dt_user.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
                 GROUP BY dt_inlet_info.dt_name, dt_inlet_info.dt_id
                 """

        order_by_query = ' ORDER BY %s DESC' % (order_by)
        _query += order_by_query

        _query += ' offset %(offset)s rows fetch next 10 rows only;'

        data = self.db.selectSQL(_query,
                                 {"create_at_start": create_at_start,
                                  "create_at_end": create_at_end,
                                  "chain_name": self.db.escape(chain_name),
                                  "chain_id": self.db.escape(chain_id),
                                  "dt_id": self.db.escape(dt_id),
                                  'offset': offset},
                                 fetchone=False)

        if data:
            data = self.deal_data(data, offset)
            ret, total = data, data[0][-1]  # 数据,总数

        raise gen.Return([ret, total])

    def deal_data(self, data, offset):
        new_data = []
        for index, sigle_row in enumerate(data):
            new_row = list(sigle_row)
            new_row.insert(0, offset + index + 1)
            new_data.append(new_row)
        return new_data
