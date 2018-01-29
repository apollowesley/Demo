#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime

from uline_risk.handlers.baseHandlers import RESTfulHandler
from uline_risk.model.uline.other import MerchantRiskInfo, MerchantRiskItem
from uline_risk.utils import db


ALI_MERCHANT_RISK_MAP = {
    'hasRisk': 1,
    'noRisk': 0,
}


class AddMerchantALIRiskHandler(RESTfulHandler):
    def prepare(self):
        self.data = self.load_json_body_data()
        self.current_time = datetime.now()

    def post(self):
        risk_result = self.data.get('risk_result')
        query_args = self.data.get('query_args')
        sys_id = self.data.get('sys_id')
        sys_type_id = self.data.get('sys_type_id')

        platform = 'alipay'

        merchant_risk_items = []
        merchant_risk_level = 0
        for each_risk_type in risk_result:
            query_key = each_risk_type.replace('riskinfo_', '')
            query_value = query_args.get(query_key, '')
            has_risk = risk_result.get(each_risk_type, '')
            risk_value = ALI_MERCHANT_RISK_MAP.get(has_risk, 0)
            if risk_value > merchant_risk_level:
                merchant_risk_level = risk_value
            risk_item = {
                'risk_type': query_key,
                'description': query_value,
                'content': json.dumps({each_risk_type: has_risk, query_key: query_value}),
                'has_risk': risk_value,
                'status': 1,
                'create_at': self.current_time,
                'update_at': self.current_time
            }
            merchant_risk_items.append(risk_item)

        merchant_risk_infos = {
            # 商户id
            'sys_id': sys_id,
            # 商户类型，目前仅有chain和mch
            'sys_type_id': sys_type_id,
            # 来源,支付宝、微信或其他平台，每个商户对应到每个来源只有一条有效记录
            'source': platform,
            # 是否有风险，0为无风险，1为有风险,2为大风险
            'has_risk': merchant_risk_level,
            # 状态, 0为无效，1为有效
            'status': 1,
            # 创建时间
            'create_at': self.current_time,
            # 更新时间
            'update_at': self.current_time
        }

        if merchant_risk_infos and merchant_risk_items:
            with db.uline_session_scope() as session:
                # 将以前的数据更新为无效
                all_actvie_platform_query = session.query(MerchantRiskInfo.id).filter(
                    MerchantRiskInfo.sys_id == sys_id).filter(MerchantRiskInfo.sys_type_id == sys_type_id).filter(
                    MerchantRiskInfo.source == platform).filter(MerchantRiskInfo.status != 0)
                session.query(MerchantRiskItem).filter(
                    MerchantRiskItem.merchant_risk_id.in_(all_actvie_platform_query)).filter(
                    MerchantRiskItem.status == 1).update({'status': 0}, synchronize_session='fetch')
                session.query(MerchantRiskInfo).filter(MerchantRiskInfo.id.in_(all_actvie_platform_query)).update(
                    {'status': 0}, synchronize_session='fetch')

                merchant_risk = MerchantRiskInfo(**merchant_risk_infos)
                session.add(merchant_risk)
                session.flush()
                merchant_risk_id = merchant_risk.id
                for each_risk_item in merchant_risk_items:
                    each_risk_item['merchant_risk_id'] = merchant_risk_id
                    session.add(MerchantRiskItem(**each_risk_item))
        response = self.generate_response_msg()
        self.write(response)
        self.finish()
