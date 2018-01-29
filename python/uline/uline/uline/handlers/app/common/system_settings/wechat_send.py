# -*- coding: utf-8 -*-
from uline.handlers.baseHandlers import CommanHandler
from tornado import gen
from tornado.web import authenticated
from uline.public import common
from uline.public import log
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchInletInfo, DtInletInfo
from uline.model.uline.info import MchPayment, DtPayment
from uline.public.constants import PAYMENT
from .form import OpenCloseWechatNews, ChoosePayment
import json
from .common import get_employee_login, auth_wx_news_open, LOCAL_HTML
from uline.public.permit import  check_permission


class NewsOperateWeb(CommanHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.employee_id = self.session["employee_id"]
        self.sys_type_code = self.session["sys_type_code"]

    def get(self):
        # 开通为2,关闭为3,未开通为初始值1
        employee = get_employee_login(self.employee_id)
        ret = auth_wx_news_open(self.sys_type_code, self.employee_id)
        html = '{}/system_settings/weChatnews.html'.format(LOCAL_HTML[self.sys_type_code])

        if ret[0] != 2:
            # self.write(json.dumps(dict(open_or_close=ret[0], code=200)))
            self.render(html, open_or_close=ret[0])
            return
        else:
            notify_payment_type = []
            if self.sys_type_code in ["mch"]:
                notify_payment_type = uline_session.query(MchPayment.payment_type, MchPayment.open_status).order_by(
                    MchPayment.payment_type).filter(MchPayment.mch_id == employee.sys_id).all()
            if self.sys_type_code in ["mr"]:
                notify_payment_type = uline_session.query(DtPayment.payment_type, DtPayment.news_push_open_status).order_by(
                    DtPayment.payment_type).filter(DtPayment.dt_id == employee.sys_id).all()
            payment_type = [[PAYMENT[str(payment)], status, payment] for payment, status in notify_payment_type]
            # payment_type = [dict(zip(["payment", "status","payment_num"], i)) for i in payment_type]
            # self.write(json.dumps(dict(data=payment_type, open_or_close=ret[0], code=200)))
            self.render(html, open_or_close=ret[0], data=payment_type)

            return


class SwitchWechatNews(CommanHandler):

    @authenticated
    def prepare(self):
        form = OpenCloseWechatNews(self)
        self.employee_id = self.session["employee_id"]
        self.sys_type_code = self.session["sys_type_code"]

        self.open_status = form.open_status.data

    def get(self):
        s_rsp = common.scc_rsp(code=200, msg='操作成功')
        try:
            employee = get_employee_login(self.employee_id)
            if self.sys_type_code in ["mch"]:
                uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == employee.sys_id).update(
                    {MchInletInfo.open_or_close: self.open_status})
            if self.sys_type_code in ["mr"]:
                uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == employee.sys_id).update(
                    {DtInletInfo.chain_wechat_news: self.open_status})
            uline_session.commit()
        except Exception as err:
            log.exception.info(err)
            s_rsp = common.f_rsp(msg='操作失败,请重试!')
        self.write(s_rsp)
        return


class ChoosePaymentType(CommanHandler):

    @authenticated
    def prepare(self):
        form = ChoosePayment(self)
        self.employee_id = self.session["employee_id"]
        self.sys_type_code = self.session["sys_type_code"]

        self.payment_type = form.payment_type.data
        self.open_status = form.open_status.data

    @gen.coroutine
    def get(self):
        # 验证是否开通
        employee = get_employee_login(self.employee_id)
        ret = auth_wx_news_open(self.sys_type_code, self.employee_id)
        if ret[0] != 2:
            rsp = common.scc_rsp(code=406, msg='操作失败,目前您未开通消息推送功能!')
            self.finish(rsp)
            return

        try:
            if self.sys_type_code in ["mch"]:
                uline_session.query(MchPayment).filter(MchPayment.mch_id == employee.sys_id,
                                                       MchPayment.payment_type == self.payment_type).update(
                    {MchPayment.open_status: self.open_status})
            if self.sys_type_code in ["mr"]:
                uline_session.query(DtPayment).filter(DtPayment.dt_id == employee.sys_id,
                                                      DtPayment.payment_type == self.payment_type).update(
                    {DtPayment.news_push_open_status: self.open_status})
            uline_session.commit()
            rsp = common.f_rsp(code=200, msg='操作成功')
        except Exception as err:
            log.exception.info(err)
            rsp = common.f_rsp(msg='操作失败,请重新尝试!')
        self.write(rsp)  # 关闭推送功能
        return
