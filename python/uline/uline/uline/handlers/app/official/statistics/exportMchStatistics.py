# -*- coding: utf-8 -*-
# 导出到xls格式
# TODO 大量数据导出可能会需要celery进行异步处理
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public import common
from datetime import timedelta, datetime
from .form import MchStatisticsSearch

from uline.backend.bank.generate_mch_statistics import generate_xls
import tcelery
tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT
from uline.public.permit import check_permission


class ExportMchStatistics(OfclAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MchStatisticsSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/official/stats/mch')
            return
        query_date = self.form.query_date.data or None
        if int(query_date) == 2:
            if not self.get_argument('create_at_start'):
                self.form.create_at_start.data = datetime.now().strftime('%Y-%m')
                _year, _month = self.form.create_at_start.data.split('-')
            else:
                self.form.create_at_start.data = self.get_argument(
                    'create_at_start')
                _year, _month = self.get_argument(
                    'create_at_start').split('-')[:2]
            self.create_at_start = datetime(int(_year), int(
                _month), 2, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
            month_ = 1 if _month in ["12", 12] else int(_month) + 1
            _year = int(_year) + 1 if _month in ["12", 12] else _year
            self.create_at_end = datetime(int(_year), month_, 1, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')

        if int(query_date) == 1:
            # 默认查询昨天的交易数据
            if not self.form.create_at_start.data:
                query_date = self.form.create_at_start.data = (common.timestamp_now().replace(
                    hour=0, minute=0, second=0) - timedelta(days=1)).date()
            else:
                query_date = common.parse_ymd(self.form.create_at_start.data)

            self.create_at_start = query_date + timedelta(days=1)
            self.create_at_end = query_date + timedelta(days=2)
            # if not self.form.create_at_start.data:
            #     self.form.create_at_start.data = common.timestamp_now()
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
        create_at_start = self.create_at_start
        create_at_end = self.create_at_end
        mch_name = self.form.mch_name.data or None
        dt_name = self.form.dt_name.data or None
        dt_id = self.form.dt_id.data or None
        mch_id = self.form.mch_id.data or None
        bk_id = self.form.bk_id.data or None
        bk_name = self.form.bk_name.data or None
        expand_type = self.form.expand_type.data or None
        order_by = self.form.order_by.data

        total_num = self.form.total_num.data or 0

        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async,
                                      args=[self.current_user, dt_name, dt_id,
                                            mch_name, mch_id,
                                            create_at_start,
                                            create_at_end,
                                            order_by, total_num, expand_type, bk_id, bk_name])

            # response = generate_xls(self.current_user, dt_name, dt_id,
            #                         mch_name, mch_id,
            #                         create_at_start, total_num)

            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async,
                               args=[self.current_user, dt_name, dt_id,
                                     mch_name, mch_id,
                                     create_at_start,
                                     create_at_end,
                                     order_by, total_num, expand_type, bk_id, bk_name])

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
