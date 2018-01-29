#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline_risk.handlers.baseHandlers import RESTfulHandler
from uline_risk.handlers.app.merchant_account.form import MerchantCreditControl
from uline_risk.model.uline.info import MchInletInfo, DtInletInfo
from uline_risk.model.uline.other import RiskControl
from uline_risk.utils import db
import json


class SettingMerchantCreditControlHandler(RESTfulHandler):

    def prepare(self):
        self.data = self.load_json_body_data()
        self.current_time = self.get_current_time()
        self.form = MerchantCreditControl(data=self.data)

    def post(self):
        self.valid_params()
        sys_id = self.form.role_id.data
        sys_type_id = self.form.role_type.data
        platform = self.form.platform.data
        action = self.form.action.data
        inlet_info = None
        with db.uline_session_scope() as session:
            if sys_type_id in ['mch', 'cs']:
                inlet_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == sys_id).first()
            elif sys_type_id in ['chain', 'dt']:
                inlet_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == sys_id).first()
            inlet_info = inlet_info.to_dict() if inlet_info else None
        if not inlet_info:
            response = self.generate_response_msg('no_merchant')
            self.write(response)
            self.finish()
            return
        with db.uline_session_scope() as session:
            db_risk_info = session.query(RiskControl).filter(RiskControl.sys_id == sys_id).filter(
                RiskControl.sys_type_id == sys_type_id).first()
            if db_risk_info:
                db_credit = db_risk_info.credit
                db_credit = json.loads(db_credit) if db_credit else {}
                db_channels = db_credit.get('channel', [])
                db_channels = db_channels if db_channels else []
                if action == 'open' and platform in db_channels:
                    db_channels.remove(platform)
                elif action == 'close' and platform not in db_channels:
                    db_channels.append(platform)
                db_credit['channel'] = db_channels if db_channels else []
                db_risk_info.credit = json.dumps(db_credit)
                db_risk_info.update_at = self.current_time
            elif not db_risk_info and action == 'close':
                risk_control_info = {
                    'sys_id': sys_id,
                    'sys_type_id': sys_type_id,
                    'credit': json.dumps({'channel': [platform]}),
                    'update_at': self.current_time,
                    'create_at': self.current_time,
                    'pay': '',
                    'settle': '',
                }
                session.add(RiskControl(**risk_control_info))
        response = self.generate_response_msg()
        self.write(response)
        self.finish()
