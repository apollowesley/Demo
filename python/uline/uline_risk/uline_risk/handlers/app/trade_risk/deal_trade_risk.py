#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime

from tornado import gen

from uline_risk.handlers.baseHandlers import RESTfulHandler, RESTfulException
from uline_risk.handlers.app.trade_risk.form import TradeRiskDealForm

from uline_risk.utils import db
from uline_risk.utils.alipay.query_alipay_mapi import query_ali_mapi

from uline_risk.public import constants

from uline_risk.model.uline.other import RiskControl, TradeRiskInfo
from uline_risk.model.uline.info import MchPayment, MchInletInfo, MchBalance
from uline_risk.model.uline.user import MchUser

from uline_risk.settings import RISK_SIGN_TYPE


class TradeRiskDeal(RESTfulHandler):
    def prepare(self):
        query_data = json.loads(self.request.body)
        self.form = TradeRiskDealForm(data=query_data)
        self.current_time = datetime.now()

    @gen.coroutine
    def post(self):
        self.valid_params()

        risk_id = self.form.risk_id.data
        handle_type = self.form.handle_type.data
        close_payments = self.form.close_payments.data
        if close_payments:
            close_payments = close_payments.split(',')
        freeze_account = self.form.freeze_account.data
        if freeze_account:
            # freeze_account = freeze_account.split(',')
            freeze_account = 1
        if handle_type == 'deal' and not close_payments and not freeze_account:
            response_info = self.generate_response_msg("no_deal_plan")
            self.write(response_info)
            self.finish()
            return

        trade_risk_info = None
        mch_info = None
        mch_user = None
        with db.uline_session_scope() as session:
            trade_risk_info = session.query(TradeRiskInfo).filter(TradeRiskInfo.id == risk_id).first()
            if trade_risk_info:
                trade_risk_info = trade_risk_info.to_dict()
                sys_id = trade_risk_info.get('sys_id', None)
                if sys_id:
                    mch_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == sys_id).first()
                    mch_info = mch_info.to_dict() if mch_info else None
                    mch_user = session.query(MchUser).filter(MchUser.mch_id == sys_id).first()
                    mch_user = mch_user.to_dict() if mch_user else None

        if not trade_risk_info:
            response_info = self.generate_response_msg("no_trade_info")
            self.write(response_info)
            self.finish()
            return

        if not mch_info or not mch_user:
            response_info = self.generate_response_msg("no_merchant_info")
            self.write(response_info)
            self.finish()
            return

        platform = trade_risk_info.get('platform', '')
        if not platform:
            response_info = self.generate_response_msg("no_platform")
            self.write(response_info)
            self.finish()
            return

        mch_id = mch_info.get('mch_id', 0)
        self.sys_type = 'cs' if mch_info.get('cs_id', '') else 'mch'
        handle_content = None
        if handle_type == 'deal':
            handle_content = self._deal_trade_risk(risk_id, mch_id, platform, close_payments, freeze_account)
        elif handle_type == 'ignore':
            handle_content = self._ignore_trade_risk(risk_id, platform)
        response_info = self.generate_response_msg()
        self.write(response_info)
        self.finish()
        # TODO 反馈给第三方,是否需要后台进行处理
        yield self.notify_third_party(handle_content, platform, trade_risk_info)

    def _deal_trade_risk(self, risk_id, mch_id, platform, close_payments, freeze_account):
        handle_content = {}

        deal_payment_message = []
        for each_payment_type in close_payments:
            deal_payment_message.append(constants.AVAILABLE_PAYMENTS_FORMAT[str(each_payment_type)])
        deal_payment_message = '关闭' + '、'.join(deal_payment_message) if deal_payment_message else ''
        deal_message_list = []
        if deal_payment_message:
            deal_message_list.append(deal_payment_message)

        close_count = False
        deal_account_message = ''
        # if platform in freeze_account:
        if freeze_account:
            close_count = True
            deal_account_message = u'冻结结算账户'
            deal_message_list.append(deal_account_message)

        if platform == 'alipay' and close_count:
            handle_content['process_code'] = '01'
        elif platform == 'alipay':
            handle_content['process_code'] = '99'

        if close_payments:
            handle_content['close_payments'] = close_payments
        if freeze_account:
            handle_content['freeze_account'] = freeze_account

        trade_risk_update_info = {
            'status': 2,
            'handler_message': ','.join(deal_message_list),
            'handle_result': json.dumps(handle_content)
        }

        with db.uline_session_scope() as session:
            # 关闭相关支付方式
            # session.query(MchPayment).filter(MchPayment.mch_id == mch_id).filter(
            # MchPayment.payment_type.in_(tuple(close_payments))).update({'activated_status': 1},
            # synchronize_session='fetch')
            session.query(MchPayment).filter(
                MchPayment.mch_id == mch_id).filter(
                    MchPayment.uline_payment_code.in_(tuple(close_payments))).update(
                        {'activated_status': 1},
                        synchronize_session='fetch')
            # 更新激活信息
            active_count = session.query(MchPayment).filter(MchPayment.activated_status == 2).count()
            activated_status = 2 if active_count else 1
            session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id).update(
                {'activated_status': activated_status}, synchronize_session='fetch')
            # 更新处理结果
            session.query(TradeRiskInfo).filter(TradeRiskInfo.id == risk_id).update(trade_risk_update_info,
                                                                                    synchronize_session='fetch')
            # todo 冻结资金账户
            if freeze_account:
                # self.freeze_accounts(session, freeze_account, mch_id)
                self.freeze_all_account(session, mch_id)
        return handle_content

    @gen.coroutine
    def notify_third_party(self, handle_content, platform, trade_risk_info):
        result = {}
        if platform == 'alipay':
            handle_content['smid'] = trade_risk_info.get('sub_mch_id', '')
            result = yield query_ali_mapi('customerrisk_send', handle_content, 'risk',
                                          requred_param_key='required_keys',
                                          crypto_type=RISK_SIGN_TYPE, charset='GBK')
        raise gen.Return(result)

    def freeze_all_account(self, session, mch_id):
        balance = session.query(MchBalance).filter(MchBalance.mch_id == mch_id).first()
        if balance:
            balance.status = 1

    def freeze_accounts(self, session, freeze_account, mch_id):
        db_risk_control = session.query(RiskControl).filter(RiskControl.sys_id == mch_id).filter(
            RiskControl.sys_type_id == self.sys_type).first()
        settle_update_info = {'channel': freeze_account}
        if db_risk_control:
            db_settle = db_risk_control.settle
            if db_settle:
                db_settle = json.loads(db_settle)
                channel_settle = db_settle.get('channel', None)
                channel_settle = channel_settle if channel_settle else []
                db_settle['channel'] = list(set(channel_settle + freeze_account))
            else:
                db_settle = json.dumps(settle_update_info)
            db_risk_control.settle = json.dumps(db_settle)
            db_risk_control.update_at = self.current_time
        else:
            risk_control_info = {
                'sys_id': mch_id,
                'sys_type_id': 'mch',
                'settle': json.dumps(settle_update_info),
                'update_at': self.current_time,
                'create_at': self.current_time
            }
            session.add(RiskControl(**risk_control_info))

    def _ignore_trade_risk(self, risk_id, platform):
        """忽略风险， 更新数据库状态，反馈支付信息"""
        with db.uline_session_scope() as session:
            session.query(TradeRiskInfo).filter(TradeRiskInfo.id == risk_id).update({'status': 3},
                                                                                    synchronize_session='fetch')
        handle_content = {}
        if platform == 'alipay':
            handle_content['process_code'] = '99'
        return handle_content

    def valid_params(self):
        if not self.form.validate():
            raise RESTfulException('params_error', error_detail=self.form.errors)
