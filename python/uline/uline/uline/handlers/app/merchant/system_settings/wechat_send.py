# -*- coding: utf-8 -*-
from uline.handlers.baseHandlers import MchAdminHandler
from tornado import gen
from tornado.web import asynchronous, authenticated
from uline.public import common
from uline.public import log
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchInletInfo
from uline.model.uline.info import MchPayment
from uline.public.constants import PAYMENT
from uline.public.permit import check_permission


class NewsOperateWeb(MchAdminHandler):
    # /sendnotify
    @authenticated
    @check_permission
    def prepare(self):
        self.query_id = self.current_user

    def get(self):
        # 开通为2,关闭为3,未开通为初始值1
        ret = uline_session.query(MchInletInfo.open_or_close).filter(
            MchInletInfo.mch_id == self.query_id).one()
        if ret[0] != 2:
            self.render('merchant/system_settings/weChatnews.html',
                        open_or_close=ret[0])  # 判断是关闭还是未开通
        else:
            notify_payment_type = uline_session.query(MchPayment.payment_type, MchPayment.open_status).order_by(
                MchPayment.payment_type).filter(MchPayment.mch_id == self.query_id).all()
            payment_type = []
            for i in notify_payment_type:
                i = list(i)
                pay_num = i[0]
                i[0] = PAYMENT[str(i[0])]
                i.append(pay_num)
                payment_type.append(i)
            self.render('merchant/system_settings/weChatnews.html',
                        data=payment_type, open_or_close=ret[0])


class SwitchWechatNews(MchAdminHandler):
    # /open
    @authenticated
    @check_permission
    def prepare(self):
        self.query_id = self.get_current_user()
        self.open_status = self.get_argument('open_status')

    def get(self):
        s_rsp = common.scc_rsp(code=200, msg='操作成功')
        try:
            uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == self.query_id).update(
                {MchInletInfo.open_or_close: self.open_status})
            uline_session.commit()
        except Exception as err:
            log.exception.info(err)
            s_rsp = common.f_rsp(code=406, msg='操作失败,请重试!')
        self.write(s_rsp)
        return


class ChoosePaymentType(MchAdminHandler):
    # /payment/?mch_id= & payment_type= & open_or_close =
    @authenticated
    @check_permission
    def prepare(self):

        self.query_id = self.get_current_user()
        self.payment_type = self.get_argument('payment_type')
        self.open_status = self.get_argument('open_status')

    # @asynchronous
    @gen.coroutine
    def get(self):
        # 验证是否开通
        ret = uline_session.query(MchInletInfo.open_or_close).filter(
            MchInletInfo.mch_id == self.query_id).one()
        if ret[0] != 2:
            rsp = common.scc_rsp(code=406, msg='操作失败,目前您未开通消息推送功能!')
            self.write(rsp)
            return

        try:
            query = uline_session.query(MchPayment.open_status).filter(MchPayment.mch_id == self.query_id,
                                                                       MchPayment.payment_type == self.payment_type).one()
            if query[0] == int(self.open_status):
                rsp = common.f_rsp(code=406, msg='same_status')
            else:
                uline_session.query(MchPayment).filter(MchPayment.mch_id == self.query_id,
                                                       MchPayment.payment_type == self.payment_type).update(
                    {MchPayment.open_status: self.open_status})
                uline_session.commit()
                rsp = common.f_rsp(code=200, msg='操作成功')
        except Exception as err:
            log.exception.info(err)
            rsp = common.f_rsp(code=406, msg='操作失败,请重新尝试!')
        self.write(rsp)  # 关闭推送功能
        return
