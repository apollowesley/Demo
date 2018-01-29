#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import json

from tornado.web import authenticated

from uline.handlers.baseHandlers import BkAdminHandler
from uline.handlers.app.bank.subsidize.form import MchSubsidizeModifyForm
from uline.public import common, discount_util
from uline.public.db import uline_session_scope
from uline.model.uline.info import MchInletInfo, Discount, DtInletInfo
from uline.model.uline.user import BkUser
from uline.public.permit import check_permission


class MchSubsidizeModifyHandler(BkAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MchSubsidizeModifyForm(self)
        self.role_id = self.form.role_id.data
        self.status = self.form.status.data
        self.weixin = self.form.weixin.data
        self.alipay = self.form.alipay.data

        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            f_rsp['error_msg'] = self.form.errors
            self.finish(f_rsp)
            return
        if not (self.weixin or self.alipay):
            f_rsp = common.f_rsp(code=406, msg=u'补贴费率小于0')
            self.finish(f_rsp)
            return
        inlet_info = False
        role_type = 'mch'
        is_bank_direct = False
        self.subsidize_info = None
        with uline_session_scope() as session:
            role_inlet_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == self.role_id).filter(
                MchInletInfo.cs_id == None).first()

            if not role_inlet_info:
                role_inlet_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == self.role_id).filter(
                    DtInletInfo.parent_id != None).first()
                role_type = 'chain'
            if role_inlet_info:
                inlet_info = True
            if role_inlet_info and role_type:
                bk_id = role_inlet_info.bk_id
                if bk_id:
                    bk_user = session.query(BkUser).filter(BkUser.bk_id == bk_id).filter(
                        BkUser.bk_type == 1).first()
                    if not bk_user:
                        is_bank_direct = False

                dt_id = role_inlet_info.dt_id if role_type == 'mch' else role_inlet_info.parent_id

                dt_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == dt_id).filter(
                    DtInletInfo.dt_type == 2).first()
                if dt_info:
                    is_bank_direct = True

                subsidize_info = session.query(Discount).filter(Discount.role_id == self.role_id).filter(
                    Discount.role == role_type).first()
                if subsidize_info:
                    self.subsidize_info = subsidize_info.to_dict()
        if not inlet_info or  not is_bank_direct:
            f_rsp = common.f_rsp(code=406, msg=u'该直连商户不存在')
            self.finish(f_rsp)
            return
        if not self.subsidize_info:
            f_rsp = common.f_rsp(code=406, msg=u'该商户不是活动商户')
            self.finish(f_rsp)
            return
        self.current_time = datetime.now()
        self.role_type = role_type

    def post(self):
        update_info = {
            'rate':json.dumps({
                'weixin': self.weixin * 100 if self.weixin else 0,
                'alipay': self.alipay * 100 if self.alipay else 0,
            }),
            'valid': self.status,
            'update_at': self.current_time,
        }
        with uline_session_scope() as session:
            session.query(Discount).filter(Discount.id == self.subsidize_info.get('id', 0)).update(update_info)
        f_rsp = common.f_rsp(code=200, msg=u'success')
        self.finish(f_rsp)
