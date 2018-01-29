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
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from uline.handlers.baseHandlers import DtAdminHandler
from .form import MerchantSearch
from datetime import timedelta

from uline.backend.dist.generate_mch_inlet_info import generate_xls
import tcelery
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT


class ExportMerchantHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantSearch(self)
        self.form.dt_id = self.current_user
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/dist/inlet/mch')

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        res = yield self.async_generate_xls()

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
            data = {"code": 406, "msg": "导出失败"}

        self.write(data)
        self.finish()

    @gen.coroutine
    def db_inlet_info(self):
        """
        """
        # 返回列表,过滤、分页
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        activated_status = self.form.activated_status.data or None
        mch_name = self.form.mch_name.data or None
        auth_status = self.form.auth_status.data or None
        total_num = self.form.total_num.data or 0
        mch_id = self.form.mch_id.data or None
        dt_sub_id = self.form.dt_sub_id.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async,
                                      args=[self.current_user, mch_name, mch_id, create_at_start,
                                            create_at_end, activated_status,
                                            auth_status, total_num, dt_sub_id])
            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async, args=[self.current_user, mch_name, mch_id, create_at_start,
                                                               create_at_end, activated_status,
                                                               auth_status, total_num, dt_sub_id])
                ret = {'order': True}
            else:
                ret = {'over_order': True}
        raise gen.Return(ret)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])