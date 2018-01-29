# -*- coding: utf-8 -*-
'''
BEGIN
获取结算银行信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import tornado.web
import tornado.gen
import tornado.escape
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from uline.handlers.baseHandlers import OfclAdminHandler
from .form import BankInfo
from uline.public.permit import check_permission


class GetBankInfoHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = BankInfo(self)
        self.key_word = form.q.data
        self.page = form.page.data or 1

    executor = ThreadPoolExecutor(10)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.async_get_bank_info()

    @run_on_executor
    def async_get_bank_info(self):
        selDbRs = self.get_search_result()
        data = {'code': 200, 'msg': 'success', 'data': selDbRs, 'total_count': self.total}
        self.write(data)

    def get_search_result(self):
        offset = (self.page - 1) * 10
        selSql = """
                SELECT bank_no,
                bank_name,
                COUNT(*) OVER () AS total
                FROM balance_bank_info
                WHERE bank_name LIKE %s LIMIT 10
                OFFSET %s"""
        selDbRs = self.db.selectSQL(selSql, ('%' + self.key_word + '%', offset), fetchone=False)
        self.total = 0 if not selDbRs else selDbRs[0][-1]
        return [dict(id=data[0], bank_name=data[1]) for data in selDbRs]


if __name__ == '__main__':
    url = "/official/inlet/dt/bank"
    data = dict(key_word="人民银行", page=2)
