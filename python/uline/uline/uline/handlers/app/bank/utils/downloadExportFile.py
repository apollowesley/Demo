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
from os import path

from uline.handlers.baseHandlers import BkAdminHandler
thread_num = cpu_count()

from .form import OperateExportFile


class DownloadExportFileHandler(BkAdminHandler):
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
        xls = yield self.do_get_static_file()
        data = {"code": 200, "msg": "success", "data": xls}
        self.write(data)
        self.finish()

    @gen.coroutine
    def do_get_static_file(self):
        order_id = self.form.order_id.data or 0
        print order_id
        query = """select file from order_download_info where order_id=%s;"""
        ret = self.db.selectSQL(query, (order_id, ))
        static_path = path.join("/static/downloads/", str(self.current_user), ret[0])
        raise gen.Return(static_path)