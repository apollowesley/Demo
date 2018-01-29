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

from uline.handlers.baseHandlers import MchAdminHandler
thread_num = cpu_count()

from uline.public.constants import DOWNLOAD_TYPE, DOWNLOAD_STATUS


class DownloadEventsHandler(MchAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @run_on_executor
    @asynchronous
    @gen.coroutine
    @authenticated
    def get(self):
        data = yield self.do_execute()
        self.render('merchant/utils/downloadEvents.html', data=data)

    @gen.coroutine
    def do_execute(self):
        query = """select
                to_char(create_at, 'YYYY-MM-DD HH24:MI:SS'),
                type,
                file,
                status,
                order_id
                from order_download_info
                where user_id=%s and status in (1,2,3,4) order by create_at desc;"""
        ret = self.db.selectSQL(query, (self.current_user, ), fetchone=False)
        ret = [list(i) for i in ret]
        data = yield self.deal_data(ret)
        raise gen.Return(data)

    @gen.coroutine
    def deal_data(self, data):
        for d in data:
            if d[1]:
                d[1] = DOWNLOAD_TYPE[str(d[1])]
            if d[3]:
                d.append(DOWNLOAD_STATUS[str(d[3])])
        return data
