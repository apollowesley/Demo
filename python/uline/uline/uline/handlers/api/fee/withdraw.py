# -*- coding:utf-8 -*-
from __future__ import division
import json
from tornado import gen
from tornado.web import authenticated, asynchronous
from uline.public import common, log
from uline.handlers.api.public.api_handler import ApiHandler
from .form import WithdrawForm
from uline.utils.record import record_utils


class WithdrawHandler(ApiHandler):
    @authenticated
    def prepare(self):
        self.form = WithdrawForm(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)

    @gen.coroutine
    def get(self, *args, **kwargs):
        with self.db.get_db() as cur:
            try:
                role = self.get_d0_withdraw_fee(cur, self.form.role.data, self.form.role_type.data)
                self.write(json.dumps(role))
            except Exception as err:
                cur.connection.rollback()
                log.exception.info(err)
                self.write(common.f_rsp(code=406, msg='fail'))

    def get_d0_withdraw_fee(self, cursor, role, role_type):
        # 防止有人瞎传，或者搞个注入啥的
        role_types = ['dt', 'mch']

        if role_type not in role_types:
            self.write(common.f_rsp(code=406, msg='fail'))
        role_info = {}
        cursor.execute("""SELECT wx,alipay FROM d0_withdraw_fee WHERE role=%s and role_type=%s;""", (role, role_type))
        ret = cursor.fetchone()

        if ret:
            role_info['wx'] = ret[0]
            role_info['alipay'] = ret[1]

        sql = "select data_json from change_record where status in (1, 4) and {id}_id = %s order by id desc;"
        cursor.execute(sql.format(id=role_type), (role,))
        query_change_record_json = cursor.fetchone()
        # 检查是否有变更金额, 如果有，则更新信息
        if query_change_record_json:
            role_record = json.loads(query_change_record_json[0]).get('role', None)
            if role_record:
                role_info.update(role_record)
        wx = role_info.get('wx', None)
        alipay = role_info.get('alipay', None)
        role_info['wx'] = wx / 100 if wx else wx
        role_info['alipay'] = alipay / 100 if alipay else alipay
        return role_info
