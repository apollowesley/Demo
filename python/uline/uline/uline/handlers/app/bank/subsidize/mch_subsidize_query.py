#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated

from uline.handlers.baseHandlers import BkAdminHandler
from uline.handlers.app.bank.subsidize.form import MchSubsidizeDetailForm
from uline.public.db import uline_session_scope
from uline.model.uline.info import MchInletInfo, DtInletInfo, Discount
from uline.model.uline.user import BkUser
from uline.public import common, discount_util
from uline.public.permit import check_permission


class MchSubsidizeInfo(BkAdminHandler):
    """
    新增活动商户时，查询商户信息
    """

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MchSubsidizeDetailForm(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)

    def get(self):
        role_id = self.form.role_id.data

        role_inlet_info = None
        role_type = 'mch'
        subsidize_info = None
        is_bank_direct = False
        if role_id:
            with uline_session_scope() as session:
                role_inlet_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == role_id).filter(
                    MchInletInfo.cs_id == None).first()

                if not role_inlet_info:
                    role_inlet_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == role_id).filter(
                        DtInletInfo.parent_id != None).first()
                    role_type = 'chain'

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

                    subsidize_info = session.query(Discount).filter(Discount.role_id == role_id).filter(
                        Discount.role == role_type).first()
                    if subsidize_info:
                        subsidize_info = subsidize_info.to_dict()
                    role_inlet_info = role_inlet_info.to_dict()

        if not role_inlet_info or not is_bank_direct:
            f_rsp = common.f_rsp(code=406, msg='该直连商户不存在')
            self.finish(f_rsp)
            return

        if subsidize_info:
            f_rsp = common.f_rsp(code=406, msg='该商户已是活动商户')
            self.finish(f_rsp)
            return

        role_info = {
            'name': role_inlet_info['mch_name'] if role_type == 'mch' else role_inlet_info['dt_name'],
            'shortname': role_inlet_info['mch_shortname'] if role_type == 'mch' else role_inlet_info['dt_short_name']
        }
        s_rsp = common.scc_rsp(code=200, msg='success', **role_info)
        self.write(s_rsp)
