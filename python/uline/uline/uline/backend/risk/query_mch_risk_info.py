#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from uline.backend.base import BaseTask
from uline.public import log, db
from uline.backend.celery import app
from uline.utils.alipay import query_alipay_mapi
from uline.settings import RISK_SIGN_TYPE
from uline.utils.risk_api import risk_api_util

ALI_MERCHANT_RISK_MAP = {
    'hasRisk': 1,
    'noRisk': 0,
}


@app.task(base=BaseTask, bind=True, max_retries=5)
def query_merchant_risk_info(self, sys_id, sys_type_id, query_dict):
    """
    请求所有围餐商户进件门店的处理结果
    """
    log.uline_celery.info('query_merchant_risk_info,{},{},{}'.format(sys_id, sys_type_id, query_dict))
    try:
        if not query_dict or not sys_id or not sys_type_id:
            return

        ali_risk_key_map = {
            'id_card_no': 'cert_no',
            'balance_account': 'bank_card_no',
            'license_num': 'business_license_no'
        }
        query_args = {ali_risk_key_map[key]: query_dict[key] for key in query_dict}
        query_args['risk_type'] = ','.join(['riskinfo_{}'.format(key) for key in query_args])
        result = query_alipay_mapi.query_ali_mapi_block('customerrisk_query', query_args, 'risk',
                                                        requred_param_key='required_keys',
                                                        crypto_type=RISK_SIGN_TYPE, charset='GBK')
        # {u'msg': u'Success', u'code': u'10000',
        #  u'risk_result':
        # u'{"riskinfo_cert_no":"hasRisk","riskinfo_business_license_no":"noRisk","riskinfo_bank_card_no":"hasRisk"}',
        #  u'risk_result_desc': u'{"hasRisk":"\u6709\u98ce\u9669","noRisk":"\u65e0\u98ce\u9669"}'}
        risk_result = result.get('risk_result') if result.get('code') in ['10000', 10000] else ''
        if not risk_result:
            log.uline_celery.info('query alipay failed')
            raise Exception('query alipay failed')
        if risk_result:
            risk_result = json.loads(risk_result)
            query_params = {}
            query_params["risk_result"] = risk_result
            query_params["query_args"] = query_args
            query_params["sys_id"] = sys_id
            query_params["sys_type_id"] = sys_type_id
            result = risk_api_util.query_risk_api_block("alipay_merchant_risk_add", method="POST", body=query_params)
            is_success, msg = risk_api_util.check_response(result)
            if not is_success:
                raise Exception(msg)
        log.uline_celery.info('query_merchant_risk_info end')
    except Exception as exc:
        log.uline_celery.exception('query alipay risk  merchant error')
        log.uline_celery.exception(exc)
        self.uline_session.rollback()
        self.retry(exc=exc)


if __name__ == '__main__':
    db.initdb()
    biz_content = {"balance_account": '6222023202018409853', 'license_num': "31339",
                   "id_card_no": "411722197303195710"}
    query_merchant_risk_info(100000665278, 'mch', biz_content)
    query_merchant_risk_info(10000228326, 'chain', biz_content)
