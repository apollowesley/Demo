#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: batch_inlet_wx.py
# datetime: 2017/5/22 19:50
# description: 批量将存量商户进件到微信，支付方式

import functools
import sys
import logging
import os

from tornado import gen, ioloop
from tornado.options import define, options

from uline.model.uline.info import MchPayment, MchInletInfo, DtInletInfo, MchInletToWxInfo
from uline.model.uline.user import MchUser
from uline.public import common
from uline.public.db import initdb
from uline.public.db import uline_session_scope
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA
)

from uline.utils.wxpay import query_wx

define('dt_id', default='', help='run on the given port', type=int)
define('mch_id', default='', help='run on the given port', type=int)

WX_PAYTYPE = [1, 2, 3, '1', '2', '3']
WX_APP_PAYTYPE = [4, '4']
ALI_PAYTYPE = [7, 8, 9, '7', '8', '9']

logger = logging.getLogger('batch_inlet_wx_new')

file_path = os.path.dirname(__file__)
filelog = logging.FileHandler(file_path + '/batch_inlet_wx_new.log')
filelog.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
filelog.setFormatter(formatter)
logger.addHandler(filelog)

consolelog = logging.StreamHandler()
consolelog.setLevel(logging.DEBUG)
logger.addHandler(consolelog)


@gen.coroutine
def deal_with_variables(dt_id='', mch_id=''):
    initdb()
    failed_mchs = list()
    with uline_session_scope() as session:
        if mch_id:
            success = yield inlet_mch2wx(session, mch_id)
            if not success:
                failed_mchs.append(mch_id)
            session.commit()
        elif dt_id:
            yield dt_inlet_mch_2wx(session, dt_id, None)
        else:
            yield inlet_all_mch_2wx(session)

            pass
    logger.info('exiting.....\n\n\n')
    sys.exit()


@gen.coroutine
def inlet_all_mch_2wx(session):
    dts = session.query(DtInletInfo).all()
    for each_dt_info in dts:
        logger.info('start inlet dt_id:{}'.format(each_dt_info.dt_id))
        yield dt_inlet_mch_2wx(session, each_dt_info.dt_id, each_dt_info)


@gen.coroutine
def dt_inlet_mch_2wx(session, dt_id, dt_info):
    if not dt_info:
        dt_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == int(dt_id)).first()
    err_msg = ''
    failed_mchs = list()
    if not dt_info:
        err_msg = '没有相关渠道商:{}'.format(dt_id)
        logger.error(err_msg)
        raise gen.Return(False)
    last_id = 0
    page_size = 100
    while True:
        mch_infos = session.query(MchInletInfo).filter(MchInletInfo.dt_id == dt_id,
                                                       MchInletInfo.mch_id > last_id).order_by(
            MchInletInfo.mch_id.asc()).limit(page_size).all()
        if not mch_infos:
            break
        for each_mch_inlet in mch_infos:
            has_wx_pay, has_wx_app_pay, has_ali_pay = check_wx_paytype(session, each_mch_inlet.mch_id)
            inlet_result = yield _inlet_to_wx(session, dt_info, each_mch_inlet, has_wx_pay, has_wx_app_pay)
            if not inlet_result:
                failed_mchs.append(each_mch_inlet.mch_id)
            if each_mch_inlet.mch_id > last_id:
                last_id = each_mch_inlet.mch_id
            session.commit()
    if failed_mchs:
        logger.error('失败的商户号')
        logger.error(failed_mchs)


@gen.coroutine
def inlet_mch2wx(session, mch_id, dt_info=None):
    mch_inlet_info = session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id).first()

    has_wx_pay, has_wx_app_pay, has_ali_pay = check_wx_paytype(session, mch_id)
    if not dt_info:
        dt_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == mch_inlet_info.dt_id).first()
    # 如果没有相关渠道商信息，则查询渠道商信息
    if not dt_info:
        logger.error('没有对应的渠道商信息')
        raise gen.Return(False)

    result = yield _inlet_to_wx(session, dt_info, mch_inlet_info, has_wx_pay, has_wx_app_pay)

    raise gen.Return(result)


def check_wx_paytype(session, mch_id):
    mch_payments = session.query(MchPayment).filter(MchPayment.mch_id == int(mch_id)).all()

    has_wx_pay, has_wx_app_pay, has_ali_pay = False, False, False

    for each_payment in mch_payments:
        paytype = each_payment.payment_type
        if paytype in WX_PAYTYPE:
            has_wx_pay = True
        if paytype in WX_APP_PAYTYPE:
            has_wx_app_pay = True
        if paytype in ALI_PAYTYPE:
            has_ali_pay = True
    return has_wx_pay, has_wx_app_pay, has_ali_pay


@gen.coroutine
def _inlet_to_wx(session, dt_info, mch_inlet_info, has_wx_pay, has_wx_app_pay):
    logger.info('开始进件到微信,商户号id: {}'.format(mch_inlet_info.mch_id))
    mch_user_info = session.query(MchUser).filter(MchUser.mch_id == mch_inlet_info.mch_id).first()
    if has_wx_pay and not dt_info.wx_channel_id:
        logger.error('渠道商没有微信渠道号，但子商户有微信支付js类支付方式,dt_id:{},mch_id:{}'.format(
            mch_inlet_info.mch_id, dt_info.dt_id))
        raise gen.Return(False)

    if has_wx_app_pay and not dt_info.wx_app_channel_id:
        logger.error('渠道商没有微信app渠道号，但子商户有微信支付app支付方式,dt_id:{},mch_id:{}'.format(
            mch_inlet_info.mch_id, dt_info.dt_id))
        raise gen.Return(False)

    query_info = {
        "merchant_name": mch_inlet_info.mch_name,
        "merchant_shortname": mch_inlet_info.mch_shortname,
        "service_phone": mch_inlet_info.service_phone,
        'contact': mch_inlet_info.contact,
        "contact_phone": mch_inlet_info.mobile,
        "contact_email": mch_inlet_info.email,
        "business": mch_inlet_info.wx_ind_code,
        "merchant_remark": mch_inlet_info.mch_id
    }

    if has_wx_pay and not has_success_inleted(session, mch_inlet_info.mch_id, 1):
        query_info['channel_id'] = dt_info.wx_channel_id
        success, wx_result = yield inlet2wx_reg(session, query_info)

        # TODO(leiyutian) 是否修改原有的wx_sub_id
        if not success:
            raise gen.Return(False)
        sub_mch_id = wx_result.get('sub_mch_id', '')
        if sub_mch_id and mch_inlet_info.wx_sub_mch_id != sub_mch_id:
            mch_user_info.wx_sub_mch_id = sub_mch_id
    if has_wx_app_pay and not has_success_inleted(session, mch_inlet_info.mch_id, 2):
        query_info['channel_id'] = dt_info.wx_app_channel_id
        success, wx_result = yield inlet2wx_app(session, query_info)
        # TODO(leiyutian) 是否修改原有的wx_sub_id
        if not success:
            raise gen.Return(False)
        sub_mch_id = wx_result.get('sub_mch_id', '')
        if sub_mch_id and mch_user_info.wx_app_channel_id != sub_mch_id:
            mch_user_info.wx_app_channel_id = sub_mch_id
    session.flush()
    raise gen.Return(True)


def has_success_inleted(session, mch_id, pay_channel):
    """
    判断是否已经被成功进件过
    """
    record = session.query(MchInletToWxInfo).filter(MchInletToWxInfo == mch_id, MchInletToWxInfo.inlet_result == 2,
                                                    MchInletToWxInfo.channel_id.isnot(None),
                                                    MchInletToWxInfo.pay_rate_channel == pay_channel).first()
    return True if record else False


@gen.coroutine
def inlet2wx_reg(session, query_info):
    args = {
        "appid": APPID,
        "mch_id": WX_MCH_ID,
    }
    query_info.update(args)
    wx_result = yield query_wx.create_wx_mch(query_info, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
    is_success, err_msg = deal_wx_result(wx_result)
    if err_msg:
        logger.error(err_msg)
    add_inlet_wx_record(session, query_info, wx_result, is_success, 1)
    raise gen.Return((is_success, wx_result))


@gen.coroutine
def inlet2wx_app(session, query_info):
    args = {
        "appid": WX_APP_APPID,
        "mch_id": WX_APP_MCH_ID,
    }
    query_info.update(args)
    wx_result = yield query_wx.create_wx_mch(query_info, WXPAY_APP_KEY, WX_APP_PRIVATE_KEY, WX_APP_PUB_KEY,
                                             WX_APP_ROOT_CA)
    is_success, err_msg = deal_wx_result(wx_result)
    if err_msg:
        logger.error(err_msg)
    add_inlet_wx_record(session, query_info, wx_result, is_success, 2)
    raise gen.Return((is_success, wx_result))


def add_inlet_wx_record(session, query_info, wx_result, is_success, rate_channel):
    inlet_to_wx_info = MchInletToWxInfo()
    inlet_to_wx_info.mch_id = query_info['merchant_remark']
    inlet_to_wx_info.return_code = wx_result['return_code']
    inlet_to_wx_info.return_msg = wx_result['return_msg']
    inlet_to_wx_info.result_code = wx_result['result_code']
    inlet_to_wx_info.result_msg = wx_result['result_msg']
    inlet_to_wx_info.create_at = common.timestamp_now()
    inlet_to_wx_info.inlet_result = 2 if is_success else 1
    inlet_to_wx_info.channel_id = query_info['channel_id']
    inlet_to_wx_info.pay_rate_channel = rate_channel
    inlet_to_wx_info.inlet_type = 1
    session.add(inlet_to_wx_info)


def deal_wx_result(wx_result):
    # error_msg = ''
    if wx_result.get('return_code', 'FAIL') == 'FAIL':
        error_msg = wx_result.get('return_msg', 'FAIL')
        return False, error_msg
    if wx_result.get('result_code', 'FAIL') == 'FAIL':
        error_msg = wx_result.get(
            'err_code_des', 'FAIL') if 'err_code_des' in wx_result else wx_result.get('result_msg', 'FAIL')
        return False, error_msg
    return True, ''


if __name__ == "__main__":
    options.parse_command_line()
    dt_id = options.dt_id
    mch_id = options.mch_id
    logger.info(common.timestamp_now())
    logger.info("dt_id:{}, mch_id:{}".format(dt_id, mch_id))
    tips = ''
    if dt_id and mch_id:
        tips = '确定将渠道商id为{}旗下商户号id为{}的商户进件到微信？(y/n)'.format(dt_id, mch_id)
    elif dt_id and not mch_id:
        tips = '确定将渠道商id为{}旗下的所有商户进件到微信？(y/n)'.format(dt_id)
    elif not dt_id and mch_id:
        tips = "确定将商户号id为{}的商户进件到微信？(y/n)".format(mch_id)
    else:
        tips = "确定将平台下所有商户进件到微信？(y/n)".format()

    sure_operator = raw_input(tips)
    if sure_operator not in ['y', 'Y']:
        logger.info('exit...\n\n\n\n')
        sys.exit()

    func_inlet = functools.partial(deal_with_variables, dt_id=dt_id, mch_id=mch_id)
    ioloop_instance = ioloop.IOLoop.current()
    ioloop_instance.run_sync(func_inlet)
    ioloop_instance.start()
