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
from uline.handlers.baseHandlers import MchAdminHandler
from .form import MerchantRefundSearch
from datetime import timedelta

from uline.backend.merchant.generate_mch_refund_info import generate_xls
import tcelery
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT


class ExportMerchantRefundHandler(MchAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantRefundSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/merchant/transaction/refund')

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        res = yield self.async_get_xls()

    @gen.coroutine
    def async_get_xls(self):
        ret = yield self.db_inlet_info()

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
    def db_inlet_info(self):
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None

        out_trade_no = self.form.out_trade_no.data or None
        mch_trade_no = self.form.mch_trade_no.data or None
        transaction_id = self.form.transaction_id.data or None

        refund_status = self.form.refund_status.data or None

        mch_refund_no = self.form.mch_refund_no.data or None
        out_refund_no = self.form.out_refund_no.data or None
        refund_id = self.form.refund_id.data or None

        channel = self.form.channel.data or None
        total_num = self.form.total_num.data or 0

        if create_at_end:
            create_at_end += timedelta(days=1)

        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async, args=[self.current_user, create_at_start, create_at_end,
                                                                      out_trade_no, mch_trade_no, transaction_id,
                                                                      refund_status,
                                                                      mch_refund_no, out_refund_no, refund_id,
                                                                      channel, total_num])
            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async,
                               args=[self.current_user, create_at_start, create_at_end,
                                     out_trade_no, mch_trade_no, transaction_id, refund_status,
                                     mch_refund_no, out_refund_no, refund_id,
                                     channel, total_num])
                ret = {'order': True}
            else:
                ret = {'over_order': True}
        raise gen.Return(ret)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])
