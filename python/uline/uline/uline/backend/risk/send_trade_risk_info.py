#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from tornado.httpclient import HTTPClient
from uline.backend.base import BaseTask
from uline.public import log, db, common
from uline.backend.celery import app
from uline.public import trade_risk_util
from uline.settings import env, RISK_NOTIFY_EMAIL, MESSAGE_URL


TRADE_RISK_NOTIFY = u"""
{platform}接口新推送一条交易风险信息，详情如下：
创建时间: {create_at}
商户编号: {mch_id}
商户名称: {mch_name}
商户简称: {mch_shortname}
所属渠道名称: {dt_name}
所属渠道编号: {dt_id}
信息来源: {platform}
第三方商户编号: {sub_mch_id}
风险类型: {risk_type}
风险情况描述: {description}
被投诉交易样例: {out_trade_no}"""

PLATFORMS = {
    'weixin': '微信',
    'alipay': '支付宝',
}


@app.task(base=BaseTask, bind=True, max_retries=5)
def send_trade_risk_email(self, risk_id):
    risk_info = {}
    with db.uline_session_scope() as session:
        trade_risk_util.get_trade_risk_info(session, {'risk_id': risk_id}, fetchone=True)
        count, db_risk_info = trade_risk_util.get_trade_risk_info(session, {'risk_id': risk_id}, fetchone=True)
        if db_risk_info:
            risk_info = {key: getattr(db_risk_info, key, '') for key in db_risk_info.keys()}
    if not risk_info:
        log.uline_celery.info('no trade risk info, risk_id:{}'.format(risk_id))
        return
    risk_info['create_at'] = common.datetime_to_str(risk_info['create_at'])
    risk_info['platform'] = PLATFORMS[risk_info['platform']]
    data = {
        'env': env,
        'reciver': RISK_NOTIFY_EMAIL,
        'title': u'新的交易风险信息',
        'body': TRADE_RISK_NOTIFY.format(**risk_info)
    }
    http_client = HTTPClient()
    url = MESSAGE_URL + '/v1/email'
    response = http_client.fetch(url, body=json.dumps(data), method='POST')

    if response and response.body == '2':
        log.uline_celery.info('send trade risk notify email success, trade risk id:{}'.format(risk_id))
    else:
        log.uline_celery.info('send trade risk notify email fail, trade risk id:{}'.format(risk_id))
        raise Exception('send trade notify email fail')


if __name__ == '__main__':
    db.initdb()
    send_trade_risk_email(2)
