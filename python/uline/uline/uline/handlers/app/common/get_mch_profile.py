#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline.handlers.baseHandlers import CommanHandler
from sqlalchemy import cast, String, null
from .form import query_mch_id
from uline.public import log, common
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchInletInfo, DtInletInfo


class Getmchprofiles(CommanHandler):

    def prepare(self):
        form = query_mch_id(self)
        if not form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
            return
        self.charac_sign = int(self.get_argument("charac_id"))  # 后台角色 1银行,5官方, 2渠道商,3连锁商户
        self.query_charac = str(self.get_argument("query_charac"))  # 查询角色 1渠道商,2商户,3门店
        self.query_id_name = self.get_argument("id_name")  # 查询id_name

    def get(self):

        if int(self.query_charac) == 1:
            res = self.dt_query()
        elif int(self.query_charac) == 3:
            res = self.mch_query()
        else:
            res_chain = self.dt_query()
            res_mch = self.mch_query()
            res = res_chain + res_mch
        ret = [dict(zip(['id', 'name'], i)) for i in res] if res else []
        data = {"data": ret}
        self.write(data)

    # 查询渠道商,连锁商户
    def dt_query(self):
        res_dt = uline_session.query(DtInletInfo.dt_id, DtInletInfo.dt_name)
        if self.query_id_name.isdigit():
            res = res_dt.filter(cast(DtInletInfo.dt_id, String).like('%' + self.query_id_name + '%'))
        else:
            res = res_dt.filter(DtInletInfo.dt_name.like('%' + self.query_id_name + '%'))
        if int(self.query_charac) == 1:
            res = res.filter(DtInletInfo.parent_id == None)
        if int(self.query_charac) == 2:
            res = res.filter(DtInletInfo.parent_id != None)
        if self.charac_sign == 2:
            res = res.filter(DtInletInfo.parent_id == self.get_user()[str(self.charac_sign)])
        res = res.all()
        return res

    # 查询商户或门店
    def mch_query(self):
        res_mch = uline_session.query(MchInletInfo.mch_id, MchInletInfo.mch_name)
        if self.query_id_name.isdigit():
            res = res_mch.filter(cast(MchInletInfo.mch_id, String).like('%' + self.query_id_name + '%'))
        else:
            res = res_mch.filter(MchInletInfo.mch_name.like('%' + self.query_id_name + '%'))
        if int(self.query_charac) == 2:
            res = res.filter(MchInletInfo.cs_id == None)
        if int(self.query_charac) == 3:
            res = res.filter(MchInletInfo.cs_id != None)
        if self.charac_sign == 2:
            res = res.filter(MchInletInfo.dt_id == self.get_user()[str(self.charac_sign)])
        if self.charac_sign == 3:
            res = res.filter(MchInletInfo.cs_id == self.get_user()[str(self.charac_sign)])
        res = res.all()
        return res
