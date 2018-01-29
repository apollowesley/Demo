# -*- coding: utf-8 -*-
# TODO 大量数据导出可能会需要celery进行异步处理
from __future__ import division
from tornado import gen
from tornado.web import asynchronous, authenticated
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from .form import TotalStatisticsSearch
from uline.handlers.baseHandlers import IntBkAdminHandler as BkAdminHandler

from datetime import timedelta
from uline.public import common

from uline.backend.inter_bank.generate_dist_transaction_stat_info import generate_xls
import tcelery
from uline.public.permit import check_permission
tcelery.setup_nonblocking_producer()
thread_num = cpu_count()


class ExportdistTransactionStatisticHandler(BkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = TotalStatisticsSearch(self)
        self.dt_id = self.get_argument('dt_id')
        # 查询参数不合法
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        res = yield self.async_get_xls()

    @gen.coroutine
    def async_get_xls(self):
        xls_path = yield self.db_transaction_stats()
        if xls_path:
            data = {"code": 200, "msg": "success", "data": str(xls_path)}
        else:
            data = {"code": 406, "msg": "fail"}
        self.write(data)
        self.finish()

    @gen.coroutine
    def db_transaction_stats(self):
        query_date = self.form.query_date.data
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        # if create_at_end:
        #     create_at_end += timedelta(days=1)

        response = yield gen.Task(generate_xls.apply_async, args=[self.dt_id, create_at_start, create_at_end, query_date])
        ret = response.result
        if isinstance(ret, dict):
            ret = False
        raise gen.Return(ret)
