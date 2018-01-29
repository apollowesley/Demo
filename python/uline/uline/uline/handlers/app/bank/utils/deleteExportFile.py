# -*- coding: utf-8 -*-
'''
BEGIN
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

from uline.handlers.baseHandlers import BkAdminHandler
thread_num = cpu_count()

from .form import OperateExportFile
from uline.public import log


class DeleteExportFileHandler(BkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    def prepare(self):
        self.form = OperateExportFile(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/bank/utils/download')

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        res = yield self.async_do_execute()

    @gen.coroutine
    def async_do_execute(self):
        data = {"code": 200, "msg": "success"}
        try:
            order_id = self.form.order_id.data or 0
            query = """update order_download_info set status=5 where order_id=%s;"""
            self.db.executeSQL(query, (order_id,))
        except Exception as err:
            log.exception.info(err)
            data = {"code": 406, "msg": "fail"}
        self.write(data)
        self.finish()
