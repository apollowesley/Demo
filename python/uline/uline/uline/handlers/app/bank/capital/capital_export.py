# -*- coding: utf-8 -*-
'''
BEGIN
获取商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
# 导出到xls格式
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from uline.handlers.baseHandlers import BkAdminHandler
from .form import MerchantWithdrawSearch
from datetime import timedelta
from uline import settings

from uline.backend.common.generate_capital_info import generate_xls
import tcelery

tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT
from uline.public.permit import check_permission


class CapitalExportHandler(BkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantWithdrawSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/bank/capital/mch')

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        res = yield self.async_generate_xls()

    @gen.coroutine
    def async_generate_xls(self):
        ret = yield self.db_capital_info()

        if ret.get('static_path'):
            data = {"code": 200, "msg": "success", "data": ret.get('static_path')}
        elif ret.get('order'):
            data = {"code": 201, "msg": "已经预约下载"}
        elif ret.get('over_order'):
            data = {"code": 202, "msg": "下载任务已经超过50条，请删除不需要的任务"}
        else:
            data = {"code": 406, "msg": "fail"}

        self.write(data)
        self.finish()

    @gen.coroutine
    def db_capital_info(self):
        """
        """
        # 返回列表,过滤、分页
        query_keys = ['create_at_start', 'create_at_end', 'mch_clear_no', 'channel', 'pay_status', 'mch_clear_no',
                      'mch_name', 'mch_shortname', 'mch_id', 'dt_name', 'dt_id', 'settle_card']

        query_conditions = {key: getattr(getattr(self.form, key), 'data', None) for key in query_keys}

        total_num = self.form.total_num.data or 0
        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async, args=[self.current_user, query_conditions, total_num])
            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async, args=[self.current_user, query_conditions, total_num])
                ret = {'order': True}
            else:
                ret = {'over_order': True}
        raise gen.Return(ret)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])
