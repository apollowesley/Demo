#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: resend_chain_active_email.py
# datetime: 2017/6/21 18:02
# description: 给连锁商户重新发送激活邮件
import tornado.web
import tornado.gen
import tornado.escape

from uline.handlers.baseHandlers import OfclAdminHandler
from .form import ResendChainActiveEmail
from uline.public import common, active_email
from uline.settings import env
from uline.public import log
from uline.model.uline.info import DtInletInfo
from uline.model.uline.base import uline_session
from uline.public.permit import check_permission


class ResendChainActiveEmailHandler(OfclAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        form = ResendChainActiveEmail(self)
        f_rsp = common.f_rsp(code=406, msg='fail')
        if not form.validate():
            self.finish(f_rsp)
        self.chain_id = form.chain_id.data
        self.create_at = common.timestamp_now()

    @tornado.gen.coroutine
    def get(self):
        chain_info_db = self.get_chain_info(self.db)
        send_success = False
        if chain_info_db:
            try:
                mch_info = {
                    'email': chain_info_db['email'],
                    'chain_name': chain_info_db['dt_name'],
                    'chain_id': chain_info_db['dt_id'],
                    'mch_pay_key': chain_info_db['mch_pay_key'],
                    'login_name': str(chain_info_db['dt_id']) + ".mr"
                }
                self.email = chain_info_db[0]

                # 如果商户激活邮件选择发送给渠道商则..
                if chain_info_db[4] == 2:
                    dt_email = uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == chain_info_db[5]).one()
                    mch_info['email'] = dt_email.email
                    self.email = dt_email.email

                response = yield active_email.send_active_chain_email(env, mch_info)
                if response and response.body == '2':
                    self.save_activated_mch_email_info(self.db, 'success', 2)
                    send_success = True
                else:
                    self.save_activated_mch_email_info(self.db, 'fail', 1)
            except Exception as err:
                import traceback
                traceback.print_exc(err)
                log.exception.info(err)
        if send_success:
            s_rsp = common.scc_rsp(code=200, msg='success')
        else:
            s_rsp = common.scc_rsp(code=406, msg='send failed')

        self.write(s_rsp)

    def get_chain_info(self, db):
        query = """select dt_inlet_info.email, dt_inlet_info.dt_name, dt_user.dt_id,dt_user.mch_pay_key, dt_inlet_info.activate_email_tag,dt_inlet_info.parent_id
                        from dt_user
                        inner join dt_inlet_info on dt_inlet_info.dt_id=dt_user.dt_id
                        where dt_user.dt_id=%s and dt_inlet_info.parent_id NOTNULL;"""
        result = db.selectSQL(query, (self.chain_id,), use_dict=True)
        return result

    def save_activated_mch_email_info(self, db, comment, status):
        query = """insert into activated_dt_email_info (dt_id,email,comment,status,create_at)
                values (%s, %s, %s, %s, %s)"""
        db.executeSQL(query, (self.chain_id, self.email,
                              comment, status, self.create_at))
