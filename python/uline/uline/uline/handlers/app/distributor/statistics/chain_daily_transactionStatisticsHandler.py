# -*- coding: utf-8 -*-
from __future__ import division
from collections import defaultdict
from datetime import datetime, timedelta
from tornado import gen
from tornado.web import asynchronous, authenticated
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import log, common
from .form import TotalStatisticsSearch
from uline.public.permit import check_permission


class ChainDailyTransactionHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(8)

    @authenticated
    @check_permission
    def prepare(self):
        form = TotalStatisticsSearch(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.create_at_start = form.create_at_start.data
        self.create_at_end = form.create_at_end.data
        self.chain_id = self.get_argument('chain_id')
        self.order_by = 'need_pay_time' if not form.order_by.data else form.order_by.data

        if self.create_at_end:
            self.create_at_end_search = self.create_at_end + timedelta(1)
        else:
            self.create_at_end = (
                datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
            self.create_at_end_search = (
                datetime.now() + timedelta(1)).strftime("%Y-%m-%d")

        self.create_at_end = str(self.create_at_end)

        if self.create_at_start:
            self.create_at_start_search = self.create_at_start + timedelta(1)
        else:
            self.create_at_start = (datetime.strptime(self.create_at_end, "%Y-%m-%d") - timedelta(days=6)).strftime(
                "%Y-%m-%d")
            self.create_at_start_search = (
                datetime.strptime(self.create_at_end, "%Y-%m-%d") - timedelta(days=5)).strftime(
                "%Y-%m-%d")

        self.last_create_at_start = datetime.today().strftime("%Y-%m-%d")
        self.last_create_at_end = (
            datetime.now() + timedelta(1)).strftime("%Y-%m-%d")

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        self.pageindex = int(self.get_argument("p", 1))
        data = yield self.do_execute()
        chain_id_name = yield self.get_chain_name()
        self.render('distributor/statistics/chaintransactionStatistics.html', data=data, order_by_form=self.order_by,
                    create_at_start=self.create_at_start, chain_id_name=chain_id_name, create_at_end=self.create_at_end)

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def post(self):
        self.pageindex = int(self.get_argument("p", 1))
        data = yield self.do_execute()
        chain_id_name = yield self.get_chain_name()
        self.render('distributor/statistics/chaintransactionStatistics.html', data=data, order_by_form=self.order_by,
                    create_at_start=self.create_at_start, chain_id_name=chain_id_name, create_at_end=self.create_at_end)

    @gen.coroutine
    def get_chain_name(self):

        ret = self.db.selectSQL(
            "select dt_id, dt_name from dt_user where dt_id = %s", (self.chain_id,))

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
                last_day_count = yield self.get_pay_count(cur, self.chain_id, self.last_create_at_start, self.last_create_at_end)
                total_count = yield self.get_pay_count(cursor=cur, chain_id=self.chain_id, create_at_start=None,
                                                       create_at_end=self.last_create_at_end)

                total_count_search = yield self.get_pay_count(cur, self.chain_id, self.create_at_start_search,
                                                              self.create_at_end_search)
                search_count_details = yield self.get_pay_count_detail(cur, self.chain_id, self.create_at_start_search,
                                                                       self.create_at_end_search,
                                                                       (self.pageindex - 1) * 10, page=True)
                chart_show_details = yield self.get_pay_count_detail(cur, self.chain_id, self.create_at_start_search,
                                                                     self.create_at_end_search,
                                                                     0, page=False)
            except Exception as err:
                cur.connection.rollback()
                log.exception.exception(err)
            else:
                cur.connection.commit()

        details, total_num = search_count_details
        navigate_html = self.get_navigate_html(total_num)

        last_day_count_data = dict(zip(last_day_count_fields, last_day_count))
        total_count_data = dict(zip(total_count_fields, total_count))
        total_count_search_data = dict(
            zip(total_count_search_fields, total_count_search))

        # details = yield
        # self.deal_search_count_details(search_count_details[0])

        date_range_key = common.get_date_range(
            self.create_at_start, self.create_at_end)

        for index in xrange(1, 7):
            detail = yield self.deal_search_count_charts(index, date_range_key, chart_show_details[0])
            charts.append(detail)

        data = dict(last_day_count_data=last_day_count_data, total_count_data=total_count_data,
                    total_count_search_data=total_count_search_data, details=details, charts=charts,
                    total_num=total_num, navigate_html=navigate_html)
        raise gen.Return(data)

    @gen.coroutine
    def get_pay_count(self, cursor, chain_id=None, create_at_start=None, create_at_end=None):
        '''
        :param cursor:
        :param create_at_start:
        :param create_at_end:
        :return:
        '''
        query = """select
                sum(ci.day_tx_count),
                round(sum(ci.day_tx_amount)/100, 2),
                sum(ci.day_refund_count),
                abs(round(sum(ci.day_refund_amount)/100, 2)),
                round(sum(ci.day_tx_net_amout)/100, 2),
                abs(round(sum(ci.day_profit_amount)/100, 2))
                from cs_daily_balance_info AS ci
                left join dt_inlet_info on ci.cs_id = dt_inlet_info.dt_id
                where (ci.cs_id = %(chain_id)s or %(chain_id)s is null)
               and (to_char(ci.need_pay_time, 'YYYY-MM-DD')::timestamp between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                or %(create_at_start)s is null or %(create_at_end)s is null);"""
        cursor.execute(
            query, {'chain_id': chain_id, 'create_at_start': create_at_start, 'create_at_end': create_at_end})
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def get_pay_count_detail(self, cursor, chain_id, create_at_start, create_at_end, offset, page=False):
        '''
        :param cursor:
        :param create_at_start:
        :param create_at_end:
        :return:
        '''
        query = """select
                        to_char(max(ci.need_pay_time) - INTERVAL '1 day', 'YYYY-MM-DD') as need_pay_time,
                        sum(ci.day_tx_count) as day_tx_count,
                        round(sum(ci.day_tx_amount), 2) as day_tx_amount,
                        sum(ci.day_refund_count) as day_refund_count,
                        abs(round(sum(ci.day_refund_amount), 2)) as day_refund_amount,
                        round(sum(ci.day_tx_net_amout), 2) as day_tx_net_amout,
                        abs(round(sum(ci.day_profit_amount), 2)) as day_profit_amount,
                        COUNT(*) over () as total
                        from cs_daily_balance_info AS ci
                        left join dt_inlet_info on ci.cs_id = dt_inlet_info.dt_id
                        where (ci.cs_id = %(chain_id)s or %(chain_id)s is null)
                        GROUP BY to_char(ci.need_pay_time, 'YYYY-MM-DD')
                        HAVING to_char(ci.need_pay_time, 'YYYY-MM-DD')::timestamp between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                        """
        if page:
            order_by_query = 'order by {} DESC ' \
                'OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;'.format(
                    self.order_by)
            query += order_by_query
            cursor.execute(
                query,
                {'chain_id': chain_id, 'create_at_start': create_at_start, 'create_at_end': create_at_end, 'offset': offset})
        else:
            order_by_query = 'order by {} DESC;'.format(self.order_by)
            query += order_by_query
            cursor.execute(
                query,
                {'chain_id': chain_id, 'create_at_start': create_at_start, 'create_at_end': create_at_end})
        ret = cursor.fetchall()
        ret = [(d[0], int(d[1]), d[2] / 100, int(d[3]), abs(d[4] / 100), d[5] / 100,
                d[6] / 100, int(d[7])) for d in
               ret] if ret else []
        if ret:
            ret_f = [ret, ret[0][-1]]
            raise gen.Return(ret_f)
        raise gen.Return([ret, 0])

    @gen.coroutine
    def get_default_date_dict(self, date_range):
        date_range_default = defaultdict(int)
        for d in date_range:
            date_range_default[d] = 0
        raise gen.Return(date_range_default)

    @gen.coroutine
    def deal_search_count_charts(self, index, date_range_key, search_count_details):
        '''
        collections生成的defaultdict必须初始化
        :param index:
        :param search_count_details:
        :return:
        '''
        # date_range_key = [data[0] for data in search_count_details] if search_count_details else []

        date_range_default = yield self.get_default_date_dict(date_range_key)

        day_tx_count = [(data[0], data[index])
                        for data in search_count_details]

        for k, v in day_tx_count:
            date_range_default[k] = round(date_range_default[k] + v, 2)

        raise gen.Return([[k, date_range_default[k]]
                          for k in sorted(date_range_default.keys())])

    # @gen.coroutine
    # def deal_search_count_details(self, search_count_details):
    #     date_range_default = defaultdict(list)
    #
    #     for pay_start_time, day_tx_count, day_tx_amount, day_refund_count, day_refund_amount, day_tx_net_amout, day_profit_amount, ___ in search_count_details:
    #         if not date_range_default[pay_start_time]:
    #             date_range_default[pay_start_time].extend(
    #                 [pay_start_time, day_tx_count, day_tx_amount, day_refund_count, day_refund_amount, day_tx_net_amout,
    #                  day_profit_amount])
    #         else:
    #             date_range_default[pay_start_time][1] += day_tx_count
    #             date_range_default[pay_start_time][2] += day_tx_amount
    #             date_range_default[pay_start_time][3] += day_refund_count
    #             date_range_default[pay_start_time][4] += day_refund_amount
    #             date_range_default[pay_start_time][5] += day_tx_net_amout
    #             date_range_default[pay_start_time][6] += day_profit_amount
    #     details = date_range_default.values()
    #     raise gen.Return(sorted(details, reverse=True))
