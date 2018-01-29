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
# TODO 大量数据导出可能会需要celery进行异步处理
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from uline.handlers.baseHandlers import IntBkAdminHandler
from .form import MerchantTradeSearch
from datetime import timedelta

from uline.backend.inter_bank.generate_mch_trade_info import generate_xls
import tcelery
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT, DOWNLOAD_INFO_NUM_LIMIT


class ExportMerchantTradeHandler(IntBkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantTradeSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/inter_bank/transaction/trade')

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
        complete_at_start = self.form.complete_at_start.data or None
        complete_at_end = self.form.complete_at_end.data or None

        mch_name = self.form.mch_name.data or None
        dt_name = self.form.dt_name.data or None
        dt_id = self.form.dt_id.data or None
        mch_id = self.form.mch_id.data or None
        cs_mch_shortname = self.form.cs_mch_shortname.data or None
        cs_mch_id = self.form.cs_mch_id.data or None

        out_trade_no = self.form.out_trade_no.data or None
        mch_trade_no = self.form.mch_trade_no.data or None
        wx_transaction_id = self.form.wx_transaction_id.data or None

        trade_state = self.form.trade_state.data or None
        # 因为 orders表中，微信和支付宝的支付成功状态不一致，所以当trade_state=SUCCESS，需加上TRADE_SUCCESS
        if trade_state:
            if trade_state == 'SUCCESS':
                trade_state = ('SUCCESS', 'TRADE_SUCCESS')
            else:
                trade_state = tuple(trade_state)
        else:
            trade_state = ('SUCCESS', 'TRADE_SUCCESS', 'REFUND', 'NOTPAY',
                           'CLOSED', 'REVOKED', 'USERPAYING', 'PAYERROR', '')

        trade_type = self.form.trade_type.data or None
        channel = self.form.channel.data or None
        total_num = self.form.total_num.data or 0
        if trade_type:
            if trade_type.startswith('ALIPAY'):
                channel = 'alipay'
                trade_type = trade_type[7:]
            elif trade_type.startswith('JDPAY'):
                channel = 'jdpay'
                trade_type = trade_type[6:]
            else:
                channel = 'weixin'

        # if complete_at_end:
        #     complete_at_end += timedelta(days=1)

        if total_num <= DOWNLOAD_INFO_NUM_LIMIT:
            response = yield gen.Task(generate_xls.apply_async,
                                      args=[self.current_user, dt_name, mch_name, dt_id, mch_id, complete_at_start,
                                            complete_at_end, out_trade_no, mch_trade_no, wx_transaction_id,
                                            trade_state, trade_type, channel, total_num, cs_mch_shortname, cs_mch_id])

            ret = response.result
        else:
            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                yield gen.Task(generate_xls.apply_async,
                               args=[self.current_user, dt_name, mch_name, dt_id, mch_id, complete_at_start,
                                     complete_at_end, out_trade_no, mch_trade_no, wx_transaction_id,
                                     trade_state, trade_type, channel, total_num, cs_mch_shortname, cs_mch_id])

                ret = {'order': True}
            else:
                ret = {'over_order': True}
        raise gen.Return(ret)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.current_user,))
        raise gen.Return(ret[0])
