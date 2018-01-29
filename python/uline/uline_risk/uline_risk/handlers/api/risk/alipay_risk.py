#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime

from uline_risk.model.uline.info import MchInletInfo
from uline_risk.model.uline.other import TradeRiskInfo
from uline_risk.model.uline_trade.order import Order
from uline_risk.utils.alipay import query_alipay_mapi
from uline_risk.utils.alipay.new_merchantInletToAlipay import AliEncryptionClass
from uline_risk.utils.db import uline_session_scope, trade_session_scope
from uline_risk.handlers.baseHandlers import RESTfulHandler


class AlipayTransactionRiskNotify(RESTfulHandler):
    def prepare(self):
        self.charset = self.get_argument('charset', 'utf-8')
        # 由于支付宝的字符可能是GBK,无法使用self.get_argument
        self.risk_info = {key: self.request.arguments[key][0].decode(self.charset) for key in self.request.arguments}
        sign = self.request.arguments.get('sign', [b''])[0]
        sign_info = {key: self.risk_info[key] for key in self.risk_info if
                     self.risk_info[key] and key not in ['sign', 'sign_type']}
        sorted_keys = sorted(sign_info)
        self.sign_info = '&'.join(["{}={}".format(key, sign_info[key]) for key in sorted_keys if sign_info[key]])

        need_validate = True
        if need_validate:
            valid_sign_result = AliEncryptionClass.verify(self.sign_info.encode(self.charset), sign,
                                                          query_alipay_mapi.ALI_CONFIGS.get('risk').get('pub_key_file'),
                                                          hash_type=self.get_argument('sign_type', 'RSA')
                                                          )
            if not valid_sign_result:
                self.write('sign failed')
                self.finish()
                return
        self.current_time = datetime.now()

    def get(self):
        role_id = None
        transaction_id = None
        sys_type = None
        dt_id = None

        out_trade_no = self.risk_info.get('tradeNos')

        with trade_session_scope() as trade_session:
            trade_info = trade_session.query(Order).filter(Order.out_trade_no == out_trade_no).first()
            if trade_info:
                role_id = trade_info.ul_mch_id
                transaction_id = trade_info.wx_transaction_id

        if not role_id:
            role_id = self.risk_info.get('externalId', None)
        self.risk_id = 0
        # 如果没有对应的订单记录
        with uline_session_scope() as uline_session:
            role_inlet_info = uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == role_id).first()
            if role_inlet_info:
                dt_id = role_inlet_info.dt_id
                sys_type = 'mch' if role_inlet_info.cs_id is None else 'cs'

            key_map = {
                'out_trade_no': 'tradeNos',
                'platform_pid': 'pid',
                'sub_mch_id': 'smid',
                'risk_type': 'risktype',
                'description': 'risklevel',
            }
            risk_info = {key: self.risk_info[key] for key in self.risk_info}
            trade_risk_info = {
                'sys_id': role_id,
                'sys_type_id': sys_type,
                'dt_id': dt_id,
                'transaction_id': transaction_id,
                'platform': 'alipay',
                'channel_code': None,
                'content': json.dumps(risk_info),
                'status': 1,
                'handle_result': None,
                'handler_message': None,
                'create_at': self.current_time,
                'update_at': self.current_time,
            }
            trade_risk_info.update({key: risk_info.get(key_map[key]) for key in key_map})
            trade_risk_info = TradeRiskInfo(**trade_risk_info)
            uline_session.add(trade_risk_info)
            uline_session.flush()
            self.risk_id = trade_risk_info.id
        # if risk_id:
        #     gen.Task(send_trade_risk_email.apply_async, args=[risk_id])
        self.write_response()

    def write_response(self):
        if self.risk_id:
            response = "success"
        else:
            response = "fail"
        self.write(response)
        self.finish()
