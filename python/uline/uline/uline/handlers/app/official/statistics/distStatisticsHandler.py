# -*- coding: utf-8 -*-
from __future__ import division
from tornado import gen
from tornado.web import asynchronous, authenticated
from concurrent.futures import ThreadPoolExecutor
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import log, common
from .form import DistStatisticsSearch
from datetime import timedelta, datetime
from uline.public.permit import check_permission


class DistStatisticsHandler(OfclAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = DistStatisticsSearch(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
            return

        self.query_date = 1 if not self.form.query_date.data else self.form.query_date.data
        self.create_at_start = self.form.create_at_start.data

        if int(self.query_date) == 1 and self.create_at_start and len(self.create_at_start.split('-')) == 2:
            self.query_date = 2

        self.form.create_at_start.data,\
            self.create_at_start,\
            self.create_at_end = common.query_common_date(
                self.query_date, self.create_at_start)

        self.pageindex = int(self.get_argument("p", 1))
        if not self.form.order_by.data:
            self.form.order_by.data = 'day_tx_count'

    @asynchronous
    @gen.coroutine
    def get(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number = ret[0], ret[1]
        navigate_html = self.get_navigate_html(total_number)
        self.render('official/statistics/distStatistics.html', navigate_html=navigate_html, data=data, form=self.form, query_date=int(self.query_date),
                    total_num=total_number)

    @asynchronous
    @gen.coroutine
    def post(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number = ret[0], ret[1]
        navigate_html = self.get_navigate_html(total_number)
        self.render('official/statistics/distStatistics.html', navigate_html=navigate_html, data=data, form=self.form, query_date=int(self.query_date),
                    total_num=total_number)

    @gen.coroutine
    def db_execute(self, form, offset):
        create_at_start = self.create_at_start
        create_at_end = self.create_at_end
        dt_name = form.dt_name.data or None
        dt_id = form.dt_id.data or None
        order_by = form.order_by.data
        expand_type = form.expand_type.data or None
        bk_id = form.bk_id.data or None
        bk_name = form.bk_name.data or None
        ret, total = [], 0

        _query = """SELECT dt_user.dt_name, dt_user.dt_id,
                    sum(dtb.day_tx_count) as day_tx_count,
                    round(sum(dtb.day_tx_amount)/100, 2) as day_tx_amount,
                    sum(dtb.day_refund_count) as day_refund_count,
                    abs(round(sum(dtb.day_refund_amount)/100, 2)) as day_refund_amount,
                    round(sum(dtb.day_tx_net_amout)/100, 2) as day_tx_net_amout,
                    abs(round(sum(dtb.day_profit_amount)/100, 2)) as day_profit_amount,
                 COUNT(*) OVER () AS total
                 FROM dt_daily_balance_info as dtb
                 LEFT JOIN dt_user on dtb.dt_id = dt_user.dt_id
                  LEFT JOIN dt_inlet_info on dt_inlet_info.dt_id = dt_user.dt_id
                 WHERE (dtb.need_pay_time between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp)
                 AND (dt_user.dt_name ~ E%(dt_name)s or %(dt_name)s = '')
                  AND dt_inlet_info.bk_id IN (SELECT bk_id FROM bk_user WHERE (bk_type = %(expand_type)s OR %(expand_type)s IS NULL)
                 AND  (bk_id::VARCHAR ~ E%(bk_id)s OR %(bk_id)s IS NULL)
                 AND (bk_name ~ E%(bk_name)s OR %(bk_name)s IS NULL))
                 AND (dt_user.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
                 GROUP BY dt_user.dt_name, dt_user.dt_id
                 """

        order_by_query = ' ORDER BY %s DESC' % (order_by)
        _query += order_by_query

        _query += ' offset %(offset)s rows fetch next 10 rows only;'

        data = self.db.selectSQL(_query,
                                 {"create_at_start": create_at_start,
                                  "create_at_end": create_at_end,
                                  "dt_name": self.db.escape(dt_name),
                                  "dt_id": self.db.escape(dt_id),
                                  'expand_type': expand_type,
                                  'bk_id': self.db.escape(bk_id),
                                  'bk_name': self.db.escape(bk_name),
                                  'offset': offset},
                                 fetchone=False)

        if data:
            data = common.deal_data(data, offset)
            ret, total = data, data[0][-1]  # 数据,总数

        raise gen.Return([ret, total])
