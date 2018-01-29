# -*- coding: utf-8 -*-
# 导出到xls格式
# TODO 大量数据导出可能会需要celery进行异步处理
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from uline.handlers.baseHandlers import BkAdminHandler
from uline.public import common
from datetime import timedelta
from .form import ChainStatisticsSearch

from uline.backend.bank.generate_chain_statistics import generate_xls
import tcelery
from uline.public.permit import check_permission
tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT


class ExportChainStatistics(BkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = ChainStatisticsSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/bank/stats/mch')
            return
        if not self.form.create_at_start.data:
            self.form.create_at_start.data = (
                common.timestamp_now()).strftime('%Y-%m-%d')
        if not self.form.order_by.data:
            self.form.order_by.data = 'day_tx_count'

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        res = yield self.async_get_xls()

    @gen.coroutine
    def async_get_xls(self):
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
        create_at_start = self.form.create_at_start.data + timedelta(days=1)
        create_at_end = self.form.create_at_start.data + timedelta(days=2)

        chain_name = self.form.chain_name.data or None
        dt_name = self.form.dt_name.data or None
        dt_id = self.form.dt_id.data or None
        chain_id = self.form.chain_id.data or None

        order_by = self.form.order_by.data

        total_num = self.form.total_num.data or 0

        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async,
                                      args=[self.current_user, dt_name, dt_id,
                                            chain_name, chain_id,
                                            create_at_start,
                                            create_at_end,
                                            order_by, total_num])

            # response = generate_xls(self.current_user, dt_name, dt_id,
            #                         mch_name, mch_id,
            #                         create_at_start, total_num)

            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async,
                               args=[self.current_user, dt_name, dt_id,
                                     chain_name, chain_id,
                                     create_at_start,
                                     order_by, total_num])

                ret = {'order': True}
            else:
                ret = {'over_order': True}
        raise gen.Return(ret)
        # raise gen.Return(response)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])
