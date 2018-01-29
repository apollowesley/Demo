#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from uline_risk.handlers.baseHandlers import RESTfulHandler
from uline_risk.handlers.app.merchant_account.form import MerchantRiskInfoControlForm
from uline_risk.utils.db import uline_session_scope
from uline_risk.model.uline.other import RiskControl


class GetMerchantRiskControlInfoHandler(RESTfulHandler):
    def prepare(self):
        self.form = MerchantRiskInfoControlForm(self)

    def get(self):
        self.valid_params()
        sys_id = self.form.sys_id.data
        sys_type_id = self.form.sys_type_id.data.decode("utf8")
        risk_info = {}
        with uline_session_scope() as session:
            risk_control_query = session.query(RiskControl).filter(RiskControl.sys_id == sys_id)
            risk_control_query = risk_control_query.filter(RiskControl.sys_type_id == sys_type_id)
            db_riskcontrol = risk_control_query.first()
            if db_riskcontrol:
                risk_info = db_riskcontrol.to_dict()
        settle = risk_info.get('settle', None)
        if settle:
            risk_info['settle'] = json.loads(settle)
        settle = risk_info.get('credit', None)
        if settle:
            risk_info['credi'] = json.loads(settle)
        response_info = {
                "risk_info": risk_info,
        }
        response = self.generate_response_msg(**response_info)
        self.write(response)
        self.finish()
