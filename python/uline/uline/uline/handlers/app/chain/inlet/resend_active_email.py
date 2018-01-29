#!/usr/bin/env python
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

from uline.handlers.baseHandlers import DtAdminHandler
from .form import ResendMchActiveEmail
from uline.public import common, active_email
from uline.settings import env
from uline.public import log
from uline.model.uline.info import DtInletInfo
from uline.model.uline.base import uline_session


class ResendMchActiveEmailHandler(DtAdminHandler):

    @tornado.web.authenticated
    def prepare(self):
        form = ResendMchActiveEmail(self)
        form.cs_id = self.current_user
        f_rsp = common.f_rsp(code=406, msg='fail')
        if not form.validate():
            self.finish(f_rsp)
        self.mch_id = form.mch_id.data
        self.create_at = common.timestamp_now()

    @tornado.gen.coroutine
    def get(self):
        mch_info_db = self.get_mch_info()
        s_rsp = common.scc_rsp(code=406, msg='send failed')
        if mch_info_db:
            try:
                mch_info = {
                    'email': mch_info_db[0],
                    'mch_name': mch_info_db[1],
                    'mch_id': mch_info_db[2],
                    'mch_pay_key': mch_info_db[3],
                    'login_name': str(mch_info_db[2]) + ".mch"

                }
                self.email = mch_info_db[0]

                # 如果商户激活邮件选择发送给渠道商则..
                if mch_info_db[5] == 2:
                    dt_email = uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == mch_info_db[6]).one()
                    mch_info['email'] = dt_email.email
                    self.email = dt_email.email

                if mch_info_db[4]:
                    response = yield active_email.send_active_cs_email(env, mch_info)
                else:
                    response = yield active_email.send_active_mch_email(env, mch_info)
                if response and response.body == '2':
                    self.save_activated_mch_email_info('success', 2)
                    s_rsp = common.scc_rsp(code=200, msg='success')
                else:
                    self.save_activated_mch_email_info('fail', 1)

            except Exception as err:
                import traceback
                traceback.print_exc(err)
                log.exception.info(err)

        self.write(s_rsp)

    def get_mch_info(self):
        query = """select mch_inlet_info.email,
                    mch_inlet_info.mch_name,
                    mch_user.mch_id,
                    mch_user.mch_pay_key,
                    mch_inlet_info.cs_id,
                    mch_inlet_info.activate_email_tag,
                    mch_inlet_info.dt_id
                        from mch_user
                        inner join mch_inlet_info on mch_inlet_info.mch_id=mch_user.mch_id
                        where mch_user.mch_id=%s"""
        result = self.db.selectSQL(query, (self.mch_id,))
        return result

    def save_activated_mch_email_info(self, comment, status):
        query = """insert into
                activated_mch_email_info (mch_id,email,comment,status,create_at)
                values (%s, %s, %s, %s, %s)"""
        self.db.executeSQL(query, (self.mch_id, self.email,
                                   comment, status, self.create_at))
