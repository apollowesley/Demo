# -*- coding: utf-8 -*-
from __future__ import absolute_import
from uline.backend.celery import app
from celery import platforms

# https://github.com/pika/pika/issues/663
# https://www.zhihu.com/question/37625671
# pika 0.9.14 to 0.10.0 有bug，不能正常回调返回response,降级pika
platforms.C_FORCE_ROOT = True
import requests
import urllib
from uline.backend.common import *
from uline.backend.base import BaseTask
from uline.model.uline.info import MchInletInfo, MchPayment
from uline.model.uline.user import MchUser, DtUser
from uline.model.uline.other import AuthMchInfo
from uline.utils.wxpay.util import params_to_sign
from uline.public import auth_util, constants
from uline.public.common import gen_randown_mch_pkey

from sqlalchemy.orm import load_only
import sys
import json

from tornado import gen

from uline.public import log

reload(sys)
sys.setdefaultencoding('utf-8')


# 10位报文长度+报文正文
# 报文的编码为GBK


# 商户进件回调
@app.task(base=BaseTask, bind=True, max_retries=5)
def callback_for_merchant_status(self, mch_id, status, message_id):
    # TODO 将url有效性放到外部,目前没有使用ORM不方便改
    # 状态1为审核未通过,状态2为审核通过
    log.uline_celery.debug('notify merchant status change, mch_id:%s, status:%s, message_id:%s'
                           % (mch_id, status, message_id))
    mch_inlet = self.uline_session.query(MchInletInfo).filter_by(mch_id=mch_id).first()
    notify_url = mch_inlet.notify_url
    if not notify_url:
        return
    try:
        d = {'event_type': 'check'}
        url = '?'.join([notify_url, urllib.urlencode(d)])

        mch_info = self.uline_session.query(AuthMchInfo).\
            filter_by(mch_id=mch_id).order_by(AuthMchInfo.id.desc()).first()
        comment = mch_info.comment or ''

        dt_user = self.uline_session.query(
            DtUser).filter_by(dt_id=mch_inlet.dt_id).first()
        api_key = getattr(dt_user, 'api_key', None) or '0000'

        # 获取商户审核驳回原因
        payload = {
            'mch_id': str(mch_id[0]) if isinstance(mch_id, tuple) else mch_id,
            'status': status,
            'comment': comment,
            'message_id': message_id
        }
        payload['sign'] = params_to_sign(payload, api_key)
        log.uline_celery.debug('callback url is: %s' % url)
        log.uline_celery.debug('callback data is: %s' % payload)
        log.uline_celery.debug('sign is: %s' % payload.get('sign'))
        r = requests.post(
            url, data=payload, allow_redirects=False, timeout=30)
        if r.text == '0' * 8:
            mch_inlet.notify_successed = 2
            self.uline_session.commit()
        else:
            raise Exception('mch_id:%s notify_url:%s not recieve message' % (mch_id, notify_url))
    except Exception as exc:
        log.uline_celery.exception('merchant change status error')
        self.uline_session.rollback()
        self.retry(exc=exc)


# 支付激活回调
@app.task(base=BaseTask, bind=True, max_retries=5)
def callback_for_merchant_active(self, mch_id, message_id):
    log.uline_celery.debug('notify merchant active, mch_id:%s, message_id:%s'
                           % (mch_id, message_id))
    mch_inlet = self.uline_session.query(MchInletInfo).filter_by(mch_id=mch_id).first()
    notify_url = mch_inlet.notify_url
    if not notify_url:
        return
    d = {'event_type': 'active'}
    url = '?'.join([notify_url, urllib.urlencode(d)])
    try:
        payments = self.uline_session.query(MchPayment).options(
            load_only('payment_type', 'activated_status')).filter_by(mch_id=mch_id)
        datas = []
        for p in payments:
            d = dict()
            d['pay_type'] = p.payment_type
            d['status'] = True if p.activated_status == 2 else False
            datas.append(d)

        # 获取商户审核驳回原因
        dt_user = self.uline_session.query(
            DtUser).filter_by(dt_id=mch_inlet.dt_id).first()
        api_key = getattr(dt_user, 'api_key', None) or '0000'
        data = {
            'mch_id': str(mch_id[0]) if isinstance(mch_id, tuple) else mch_id,
            'datas': json.dumps(datas),
            'message_id': message_id
        }
        data['sign'] = params_to_sign(data, api_key)
        # // 好想返回json┑(￣Д ￣)┍
        log.uline_celery.debug('callback url is: %s' % url)
        log.uline_celery.debug('callback data is: %s' % data)
        r = requests.post(url, data=data, allow_redirects=False, timeout=30)
        if r.text == '0' * 8:
            self.uline_session.commit()
        elif r.status_code in [400, 404, 401, 500]:
            pass
        else:
            raise Exception('mch_id:%s notify_url:%s not recieve message' % (mch_id, notify_url))
    except Exception as exc:
        log.uline_celery.exception('active merchant error')
        self.uline_session.rollback()
        self.retry(exc=exc)


@app.task(base=BaseTask, bind=True, max_retries=5)
def auth_mch_celery(self, bk_id, mch_id):
    result = {}
    try:
        log.uline_celery.info('start auth mch, mch_id:{}, bank_id:{}'.format(mch_id, bk_id))
        authutil = auth_util.MchAuthUtil(self.uline_session, bk_id, mch_id, validate_status=True)
        result = authutil.auth_mch()
        log.uline_celery.info('mch auth result:{}'.format(result))
    except Exception as exc:
        log.uline_celery.exception('auth merchant error')
        self.uline_session.rollback()
        self.retry(exc=exc)
    return result


@app.task(base=BaseTask, bind=True, max_retries=5)
def callback_for_mch_auth_result(self, auth_result, mch_id):
    log.uline_celery.info('call back for mch auth result: {}, mch:{}'.format(auth_result, mch_id))
    auth_status = auth_result.get('mch_status', 0)
    if auth_status in [1, 2] and auth_result.get('need_notify', False):
        message_id = gen_randown_mch_pkey(8)
        callback_for_merchant_status(mch_id, auth_status, message_id)
