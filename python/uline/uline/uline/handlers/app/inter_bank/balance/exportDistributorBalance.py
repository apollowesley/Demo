# -*- coding: utf-8 -*-
# TODO 大量数据导出可能会需要celery进行异步处理
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from uline.handlers.baseHandlers import IntBkAdminHandler as BkAdminHandler
from .form import DistributorBalanceSearch
from datetime import timedelta

from uline.backend.inter_bank.generate_dist_balance_info import generate_xls
import tcelery
from uline.public.permit import check_permission
tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT


class ExportDistributorBalanceHandler(BkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = DistributorBalanceSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/inter_bank/balance/dt')

    @gen.coroutine
    def get(self):
        # res = yield self.async_generate_xls()
        data = {"code": 407, "msg": "暂无数据"}
        self.write(data)

    @gen.coroutine
    def async_generate_xls(self):
        ret = yield self.db_inlet_info()

        if ret.get('static_path'):
            data = {"code": 200, "msg": "success",
                    "data": ret.get('static_path')}
        elif ret.get('order'):
            data = {"code": 201, "msg": "已经预约下载"}
        elif ret.get('over_order'):
            data = {"code": 202, "msg": "下载任务已经超过50条，请删除不需要的任务"}
        else:
            data = {"code": 406, "msg": "fail"}

        self.write(data)
        self.finish()

    @gen.coroutine
    def db_inlet_info(self):
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        dt_name = self.form.dt_name.data or None
        pay_status = self.form.pay_status.data or None
        total_num = self.form.total_num.data or 0
        dt_id = self.form.dt_id.data or None
        channel = self.form.channel.data or None
        balance_account = self.form.balance_account.data or None

        if create_at_end:
            create_at_end += timedelta(days=1)

        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async,
                                      args=[self.current_user, dt_name, dt_id, create_at_start,
                                            create_at_end, pay_status, total_num, channel, balance_account])
            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async, args=[self.current_user, dt_name, dt_id, create_at_start,
                                                               create_at_end, pay_status, total_num, channel, balance_account])
                ret = {'order': True}
            else:
                ret = {'over_order': True}
        raise gen.Return(ret)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])
