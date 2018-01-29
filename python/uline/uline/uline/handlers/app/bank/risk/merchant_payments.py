#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from tornado import web

from uline.handlers.baseHandlers import BkAdminHandler
from uline.handlers.app.bank.risk.form import GetMerchantPaymentsForm
from uline.public import common, db
from uline.model.uline.info import MchInletInfo, MchPayment, MchBalance
from uline.model.uline.other import RiskControl


class GetMerchantPayments(BkAdminHandler):
    @web.authenticated
    def prepare(self):
        self.form = GetMerchantPaymentsForm(self)
        if not self.form.validate():
            response_message = common.f_rsp(406, '参数错误')
            self.write(response_message)
            self.finish()

    def get(self):
        merchant_id = self.form.merchant_id.data
        with db.uline_session_scope() as session:
            paytypes_query = session.query(MchPayment)
            paytypes_query = paytypes_query.join(MchInletInfo, MchInletInfo.mch_id == MchPayment.mch_id)
            paytypes_query = paytypes_query.filter(MchPayment.mch_id == merchant_id)
            merchant_payments = [payment.to_dict() for payment in paytypes_query.all()]
            merchant_payments = [
                {
                    "uline_payment_code": payment.get("uline_payment_code", ""),
                    'payment_type': payment.get('payment_type', 0),
                    'activated_status': payment.get('activated_status', 1)
                }
                for payment in merchant_payments
            ]
            settle_info = self.get_account_status(session, merchant_id)

        merchant_info = {
            'payments': merchant_payments,
            'settle_info': settle_info
        }
        response_message = common.scc_rsp(code=200, msg='success', **merchant_info)
        self.write(response_message)

    def get_account_status(self, session, merchant_id):
        mch_balance = session.query(MchBalance).filter(MchBalance.mch_id == merchant_id).first()
        status = mch_balance.status if mch_balance and mch_balance.status else 2
        return status

    def get_merchant_settle(self, session, merchant_id):
        settle_info = {'alipay': 0, 'weixin': 0}
        risk_control_info = session.query(RiskControl).filter(RiskControl.sys_id == merchant_id).filter(
            RiskControl.sys_type_id.in_(('mch', 'cs'))).first()
        if risk_control_info:
            db_settle = risk_control_info.settle
            if db_settle:
                settle_info = json.loads(db_settle)
                frozen_channel = settle_info.get('channel', [])
                if frozen_channel:
                    settle_info.update({channel: 1 for channel in frozen_channel})
        return settle_info
