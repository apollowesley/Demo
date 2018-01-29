#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime

from uline.backend.base import BaseTask
# from uline.public import log, db
from uline.backend.celery import app
# from uline.utils.alipay import new_merchantInletToAlipay, query_alipay_mapi
# from uline.model.uline.other import MerchantRiskInfo, MerchantRiskItem

ALI_MERCHANT_RISK_MAP = {
    'hasRisk': 1,
    'noRisk': 0,
}


@app.task(base=BaseTask, bind=True, max_retries=5)
def query_merchant_risk_info(self, sys_id, sys_type_id, query_dict):
    """
    请求所有围餐商户进件门店的处理结果
    """
    print 'test'
    pass
