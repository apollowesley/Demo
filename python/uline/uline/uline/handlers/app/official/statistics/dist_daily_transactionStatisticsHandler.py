# -*- coding: utf-8 -*-
from __future__ import division
from collections import defaultdict
from datetime import datetime, timedelta
from tornado import gen
from tornado.web import asynchronous, authenticated
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import log, common
from .form import TotalStatisticsSearch
from uline.public.permit import check_permission


class DistDailyTransactionHandler(OfclAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        form = TotalStatisticsSearch(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.query_date = form.query_date.data
        self.create_at_start = form.create_at_start.data
        self.create_at_end = form.create_at_end.data
        self.dt_id = self.get_argument('dt_id')
        self.order_by = 'pay_time' if not form.order_by.data else form.order_by.data

        # 模块上日期
        self.last_create_at_start = datetime.today().strftime("%Y-%m-%d")
        self.last_create_at_end = (
            datetime.now() + timedelta(1)).strftime("%Y-%m-%d")

        self.create_at_start, \
            self.create_at_end, \
            self.create_at_start_search, \
            self.create_at_end_search = common.common_date_deal(self.query_date,
                                                                self.create_at_start, self.create_at_end)

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        self.pageindex = int(self.get_argument("p", 1))
        data = yield self.do_execute()
        dt_id_name = yield self.get_dt_name()
        self.render('official/statistics/disttransactionStatistics.html', data=data, order_by_form=self.order_by,
                    query_date=int(self.query_date),
                    create_at_start=self.create_at_start, dt_id_name=dt_id_name, create_at_end=self.create_at_end)

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def post(self):
        self.pageindex = int(self.get_argument("p", 1))
        data = yield self.do_execute()
        dt_id_name = yield self.get_dt_name()
        self.render('official/statistics/disttransactionStatistics.html', data=data, order_by_form=self.order_by,
                    query_date=int(self.query_date),
                    create_at_start=self.create_at_start, dt_id_name=dt_id_name, create_at_end=self.create_at_end)

    @gen.coroutine
    def get_dt_name(self):

        ret = self.db.selectSQL(
            "select dt_id, dt_name from dt_user where dt_id = %s", (self.dt_id,))

        raise gen.Return(ret)

    @gen.coroutine
    def do_execute(self):
        last_day_count, total_count, total_count_search, search_count_details, charts = [
            0] * 6, [0] * 6, [
            0] * 6, [], []
        last_day_count_fields = ['day_tx_count_last', 'day_tx_amount_last', 'day_refund_count_last',
                                 'day_refund_amount_last', 'day_tx_net_amout_last', 'day_profit_amount_last']
        total_count_fields = ['day_tx_count_total', 'day_tx_amount_total', 'day_refund_count_total',
                              'day_refund_amount_total', 'day_tx_net_amout_total', 'day_profit_amount_total']
        total_count_search_fields = ['day_tx_count_total', 'day_tx_amount_total', 'day_refund_count_total',
                                     'day_refund_amount_total', 'day_tx_net_amout_total', 'day_profit_amount_total']

        with self.db.get_db() as cur:
            try:
                last_day_count = yield self.get_pay_count(cur, self.dt_id, self.last_create_at_start,
                                                          self.last_create_at_end)
                total_count = yield self.get_pay_count(cursor=cur, dt_id=self.dt_id, create_at_start=None,
                                                       create_at_end=self.last_create_at_end)
                total_query_start = datetime.strptime(self.create_at_start_search, '%Y-%m-%d %H:%M:%S') + timedelta(
                    1) if int(self.query_date) == 2 else self.create_at_start_search
                total_count_search = yield self.get_pay_count(cur, self.dt_id, total_query_start,
                                                              self.create_at_end_search)
                search_count_details = yield self.get_pay_count_detail(cur, self.dt_id, self.create_at_start_search,
                                                                       self.create_at_end_search,
                                                                       (self.pageindex - 1) *
                                                                       10, self.query_date,
                                                                       page=True)

                chart_show_details = yield self.get_pay_count_detail(cur, self.dt_id, self.create_at_start_search,
                                                                     self.create_at_end_search,
                                                                     0, self.query_date, page=False)
            except Exception as err:
                cur.connection.rollback()
                log.exception.exception(err)
            else:
                cur.connection.commit()

        details, total_num = search_count_details
        if int(self.query_date) == 2:
            months = len(common.get_mon_seq(
                self.create_at_start, self.create_at_end))
            if len(chart_show_details[0]) > months:
                del chart_show_details[0][0]
            if len(details) > months:
                del details[0]
        details = common.append_start_end(details, self.query_date)

        navigate_html = self.get_navigate_html(total_num)

        last_day_count_data = dict(zip(last_day_count_fields, last_day_count))
        total_count_data = dict(zip(total_count_fields, total_count))
        total_count_search_data = dict(
            zip(total_count_search_fields, total_count_search))

        date_range_key = common.get_date_range(self.create_at_start, self.create_at_end) if int(
            self.query_date) == 1 else common.get_mon_seq(self.create_at_start, self.create_at_end)

        for index in range(1, 7):
            detail = yield common.deal_search_count_charts(index, date_range_key, chart_show_details[0])
            charts.append(detail)

        data = dict(last_day_count_data=last_day_count_data, total_count_data=total_count_data,
                    total_count_search_data=total_count_search_data, details=details, charts=charts,
                    total_num=total_num, navigate_html=navigate_html)
        raise gen.Return(data)

    @gen.coroutine
    def get_pay_count(self, cursor, dt_id=None, create_at_start=None, create_at_end=None):
        '''
        :param cursor:
        :param create_at_start:
        :param create_at_end:
        :return:
        '''
        query = """select
                    sum(di.day_tx_count),
                    round(sum(di.day_tx_amount)/100, 2),
                    sum(di.day_refund_count),
                    abs(round(sum(di.day_refund_amount)/100, 2)),
                    round(sum(di.day_tx_net_amout)/100, 2),
                    round(sum(di.day_profit_amount)/100, 2)
                    from dt_daily_balance_info AS di
                    left join dt_user on di.dt_id = dt_user.dt_id
                    where (di.dt_id = %(dt_id)s or %(dt_id)s is null)
                   and (to_char(di.need_pay_time, 'YYYY-MM-DD')::TIMESTAMP between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                    or %(create_at_start)s is null or %(create_at_end)s is null);"""
        cursor.execute(
            query, {'dt_id': dt_id, 'create_at_start': create_at_start, 'create_at_end': create_at_end})
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def get_pay_count_detail(self, cursor, dt_id, create_at_start, create_at_end, offset, date_switch, page=False):
        '''
        :param cursor:
        :param create_at_start:
        :param create_at_end:
        :return:
        '''
        query = """select
                    {switch}
                    sum(di.day_tx_count) as day_tx_count,
                    round(sum(di.day_tx_amount), 2) as day_tx_amount,
                    sum(di.day_refund_count) as day_refund_count,
                    abs(round(sum(di.day_refund_amount),2)) as day_refund_amount,
                    round(sum(di.day_tx_net_amout),2) as day_tx_net_amout,
                    round(sum(di.day_profit_amount),2) as day_profit_amount,
                    COUNT(*) over () as total
                    from dt_daily_balance_info AS di
                    left join dt_user on di.dt_id = dt_user.dt_id
                    where (di.dt_id = %(dt_id)s or %(dt_id)s is null)
                    and (to_char({date_query}, 'YYYY-MM-DD')::TIMESTAMP between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp)
                    GROUP BY  pay_time
                    """
        if page:
            query += 'order by {} DESC ' \
                     'OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;'.format(
                         self.order_by)
        else:
            query += 'order by {} DESC;'.format(self.order_by)

        switch = " to_char(di.need_pay_time - INTERVAL '1 day', 'YYYY-MM-DD') as pay_time," if int(
            date_switch) == 1 else "to_char(di.need_pay_time - INTERVAL '1 day','YYYY-MM') as pay_time,"
        date_query = "di.need_pay_time" if int(
            date_switch) == 1 else "di.need_pay_time - INTERVAL '1 day'"

        query = query.format(switch=switch, date_query=date_query)
        con_dict = {'dt_id': dt_id, 'create_at_start': create_at_start,
                    'create_at_end': create_at_end}
        if page:
            con_dict.update({'offset': offset})
        cursor.execute(query, con_dict)
        ret = cursor.fetchall()
        ret = [(d[0], int(d[1]), d[2] / 100, int(d[3]), abs(d[4] / 100), d[5] / 100,
                d[6] / 100, int(d[7])) for d in
               ret] if ret else []
        if ret:
            raise gen.Return([ret, ret[0][-1]])
        raise gen.Return([ret, 0])
