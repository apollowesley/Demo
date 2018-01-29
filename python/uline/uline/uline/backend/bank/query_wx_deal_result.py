#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: query_wx_deal_result.py
# datetime: 17/7/31 上午10:04
# description: 请求微信处理信息

from uline.backend.base import BaseTask
from uline.public import log
from uline.backend.celery import app

@app.task(base=BaseTask, bind=True, max_retries=5)
def query_wx_dine_result(self):
    """
    请求所有围餐商户进件门店的处理结果
    """
    try:
        log.uline_celery.info('start query wx dine result and deal')
    except Exception as exc:
        log.uline_celery.exception('auth merchant error')
        self.uline_session.rollback()
        self.retry(exc=exc)