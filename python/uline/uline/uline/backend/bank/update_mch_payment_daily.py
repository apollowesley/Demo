#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import traceback
from datetime import datetime, timedelta
import time
import sys
import functools

from tornado import ioloop
from tornado.httpclient import HTTPClient
from sqlalchemy import and_

from uline.public import constants, log
from uline.model.uline.info import MchInletInfo, D0WithdrawFee, MchPayment, DtInletInfo, DtPayment
from uline.model.uline.other import ChangeRecord, DailyCutRecord, ActivatedMchInfo
from uline.public.constants import ALI_PAY_TYPES, WX_PAY_TYPES
from uline.public.db import initdb
from uline.public.db import uline_session_scope
from uline.settings import PAYMENT_CACHE_CLEAR_URL

wx_d0_pays = constants.ONLINE_D0_WX_PAY_TYPES + constants.OFFLINE_D0_WX_PAY_TYPES
wx_d1_pays = constants.D1_WX_PAY_TYPES
ali_d0_pays = constants.D0_ALI_PAY_TYPES
ali_d1_pays = constants.D1_ALI_PAY_TYPES

TOCUT = 1
INCUTTING = 2
CUTTED = 3


def catch_func_exception(retry_times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log.uline_dailycut.info('start func:{}'.format(func.__name__))
            result = None
            count = -1
            has_exception = True
            retry_count = retry_times
            if retry_count < 0:
                retry_count = 0
            while has_exception and count < retry_count:
                result = None
                count += 1
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    log.uline_dailycut.exception(e)
                    has_exception = True
                else:
                    has_exception = False
            log.uline_dailycut.info('end func:{}'.format(func.__name__))
            return result, has_exception

        return wrapper

    return decorator


class PaymentsDailyCut(object):

    def __init__(self, session, current_time, lastet_update_time):
        self.uline_session = session
        self.current_time = current_time
        self.latest_update_time = lastet_update_time

    def update_and_close_mch_payment_info(self):
        # invalid_change_record_mch_ids = list()
        has_exception = True
        close_times = 0
        while has_exception and close_times < 5:
            close_times += 1
            has_exception = False
            exception_ids = []
            all_cut_record = self.uline_session.query(DailyCutRecord).distinct(DailyCutRecord.role_id).filter(
                DailyCutRecord.status == TOCUT).filter(
                DailyCutRecord.role_type == 'mch').filter(
                DailyCutRecord.update_at < self.latest_update_time).order_by(DailyCutRecord.role_id).order_by(
                DailyCutRecord.id.desc()).all()
            log.uline_dailycut.info('need daily cut mch count: {}'.format(len(all_cut_record)))
            count = 0
            for each_cut_record in all_cut_record:
                try:
                    self.update_mch_changes(each_cut_record)
                    count += 1
                    if count % 100 == 0:
                        self.uline_session.commit()
                except Exception as e:
                    self.uline_session.rollback()
                    log.uline_dailycut.exception(traceback.format_exc())
                    exception_ids.append(each_cut_record.role_id)
            self.uline_session.commit()
            if exception_ids:
                has_exception = True
                log.uline_dailycut.info('mch daily cut exception mch_id:{}'.format(exception_ids))

    # 更新支付信息，并把支付状态置为未激活
    def update_mch_changes(self, cut_record):
        mch_id = cut_record.role_id
        mch_inlet_info = self.uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id).filter(
            MchInletInfo.auth_status == constants.AUTH_STATUS_ACCEPT).first()
        if mch_inlet_info:
            change_data = json.loads(cut_record.record_json)
            update_payments = change_data.get('payment', {})
            if update_payments:
                self.close_mch_payments(mch_inlet_info.mch_id, update_payments)
        cut_record.status = INCUTTING
        # todo 更新支付缓存
        log.uline_dailycut.info('update mch success, mch_id:{}'.format(mch_id))

    def close_mch_payments(self, mch_id, changed_payments):
        payments = self.uline_session.query(MchPayment).filter(MchPayment.mch_id == mch_id).all()
        db_payments = {each_payment.payment_type: each_payment for each_payment in payments}

        for pay_type in changed_payments:
            payment_info = changed_payments.get(pay_type, {})

            payment_type = int(payment_info.get('payment_type', 0))
            action_type = payment_info.get('action_type', 2)
            db_payment = db_payments.get(payment_type, None)
            if payment_type != int(pay_type):
                continue

            if action_type in [2, 3] and db_payment:
                db_payment.update_at = self.current_time
                db_payment.daily_cut_status = 2

    def add_daily_cut_record(self, role_id, role_type, data):
        if not data:
            return
        record_json = json.dumps(data)
        daily_cut_record = self.uline_session.query(DailyCutRecord).filter(
            DailyCutRecord.role_type == role_type).filter(
            DailyCutRecord.role_id == role_id).filter(DailyCutRecord.status == TOCUT).first()
        if daily_cut_record:
            daily_cut_record.record_json = record_json
        else:
            daily_cut_record = DailyCutRecord()
            daily_cut_record.record_json = record_json
            daily_cut_record.role_id = role_id
            daily_cut_record.role_type = role_type
            daily_cut_record.status = 1
            self.uline_session.add(daily_cut_record)

    def mch_daily_cut(self):
        now_time = datetime.now()
        cut_records = self.uline_session.query(DailyCutRecord).filter(DailyCutRecord.role_type == 'mch').filter(
            DailyCutRecord.status == INCUTTING).all()
        for each_record in cut_records:
            update_datas = json.loads(each_record.record_json)
            with_draw_info = update_datas.get('withdraw', None)
            payments = update_datas.get('payment', None)
            mch_id = each_record.role_id
            mch_inlet_info = self.uline_session.query(
                MchInletInfo).filter(MchInletInfo.mch_id == mch_id).first()
            if not mch_inlet_info:
                continue
            print 'mch_daily_cut', mch_id

            bk_email = update_datas.get('bk_email', '')
            if payments:
                # 修改支付信息数据
                payments_list = self.uline_session.query(MchPayment).filter(MchPayment.mch_id == mch_id).all()
                db_payments = {}
                for payment in payments_list:
                    db_payments[payment.payment_type] = payment
                for each_type in payments:
                    update_payment_info = payments.get(each_type, None)
                    if not update_payment_info:
                        continue
                    action_type = update_payment_info.get('action_type', 2)
                    db_payment = db_payments.get(int(each_type), None)
                    if action_type == 2 and db_payment:
                        update_rate = update_payment_info.get('update_payment_rate', None)
                        if update_rate is None:
                            continue
                        db_payment.payment_rate = update_rate
                        db_payment.settle_rate = update_rate
                        # update_status = update_payment_info.get('pre_payment_status', None)
                        # if update_status:
                        #     db_payment.activated_status = update_status
                        db_payment.update_at = self.current_time
                        db_payment.daily_cut_status = 1
                    elif action_type == 3 and db_payment:
                        self.uline_session.delete(db_payment)
                    elif action_type == 1 and not db_payment:
                        payment_rate = update_payment_info.get('update_payment_rate', None)
                        if payment_rate is None:
                            continue
                        dt_payment = self.uline_session.query(DtPayment).filter(
                            DtPayment.dt_id == mch_inlet_info.dt_id).first()
                        if not dt_payment:
                            continue
                        payment = MchPayment()
                        payment.mch_id = mch_id
                        payment.payment_type = each_type
                        payment.payment_rate = payment_rate
                        payment.settle_rate = payment_rate
                        payment.activated_status = 2 if dt_payment.activated_status == 2 else 1
                        payment.create_at = now_time
                        payment.update_at = now_time
                        payment.daily_cut_status = 1
                        self.uline_session.add(payment)
                        activated_info = ActivatedMchInfo()

                        activated_info.mch_id = mch_id
                        activated_info.activated_status = 2
                        activated_info.payment_type = int(each_type)
                        activated_info.comment = constants.ACTIVATED_STATUS['2']
                        activated_info.create_at = self.current_time
                        activated_info.activated_user = bk_email
                        self.uline_session.add(activated_info)

            if with_draw_info:
                # 修改数据
                db_withdraw_info = self.uline_session.query(D0WithdrawFee).filter(D0WithdrawFee.role == mch_id).filter(
                    D0WithdrawFee.role_type == 'mch').first()
                if db_withdraw_info:
                    for each_key in with_draw_info:
                        setattr(db_withdraw_info, each_key, with_draw_info.get(each_key, None))
                else:
                    update_info = {
                        'update_at': self.current_time,
                        'role': mch_id,
                        'role_type': 'mch',
                        'create_at': self.current_time
                    }
                    update_info.update(with_draw_info)
                    self.uline_session.add(D0WithdrawFee(**update_info))

                db_payments = self.uline_session.query(MchPayment).filter(MchPayment.mch_id == mch_id).all()
                wx_withdraw = with_draw_info.get('wx') if with_draw_info.get(
                    'wx') else with_draw_info.get('wx_draw_fee')
                wx_draw_rate = with_draw_info.get('wx_draw_rate', None)
                alipay_withdraw = with_draw_info.get('alipay') if with_draw_info.get(
                    'alipay') else with_draw_info.get('ali_draw_fee')
                ali_draw_rate = with_draw_info.get('ali_draw_rate', None)
                for each_payment in db_payments:
                    # 写入手续费
                    if each_payment.uline_payment_id in ALI_PAY_TYPES:
                        if alipay_withdraw:
                            each_payment.withdraw_fee = alipay_withdraw
                        if ali_draw_rate:
                            each_payment.withdraw_rate = ali_draw_rate
                    elif each_payment.uline_payment_id in WX_PAY_TYPES:
                        if wx_withdraw:
                            each_payment.withdraw_fee = wx_withdraw
                        if wx_draw_rate:
                            each_payment.withdraw_rate = wx_draw_rate
                    self.uline_session.add(each_payment)

            has_active_payments = self.uline_session.query(MchPayment).filter(MchPayment.activated_status == 2).filter(
                MchPayment.mch_id == mch_id).count()
            self.uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == mch_id).update(
                {'activated_status': 2 if has_active_payments > 0 else 1}, synchronize_session='fetch')

            each_record.status = CUTTED
            each_record.update_at = datetime.now()
            # 更新change_record状态
            change_record_id = update_datas.get('change_record_id', None)
            if change_record_id:
                change_record = self.uline_session.query(ChangeRecord).filter(
                    ChangeRecord.id == change_record_id).first()
                if change_record:
                    change_record.status = 2


class DtDailycutUtil(object):

    def __init__(self, session, current_time, lastet_update_time):
        self.uline_session = session
        self.current_time = current_time
        self.latest_update_time = lastet_update_time
        self.role_type = 'dt'

    def update_and_close_dt_mch_payment_info(self):
        has_exception = True
        close_times = 0
        while has_exception and close_times < 5:
            close_times += 1
            has_exception = False
            exception_ids = []
            all_cut_record = self.uline_session.query(DailyCutRecord).distinct(DailyCutRecord.role_id).filter(
                DailyCutRecord.status == TOCUT).filter(
                DailyCutRecord.role_type == 'dt').filter(
                DailyCutRecord.update_at < self.latest_update_time).order_by(DailyCutRecord.role_id).order_by(
                DailyCutRecord.id.desc()).all()
            log.uline_dailycut.info('need daily cut dt count: {}'.format(len(all_cut_record)))
            count = 0
            for each_cut_record in all_cut_record:
                try:
                    self.update_dt_changes(each_cut_record)
                    count += 1
                    if count % 100 == 0:
                        self.uline_session.commit()
                except Exception as e:
                    self.uline_session.rollback()
                    log.uline_dailycut.exception(traceback.format_exc())
                    exception_ids.append(each_cut_record.role_id)
            self.uline_session.commit()
            if exception_ids:
                has_exception = True
                log.uline_dailycut.info('dt dayiy cut exception dt_id:{}'.format(exception_ids))

    def update_dt_changes(self, cut_record):
        dt_id = cut_record.role_id
        dt_inlet_info = self.uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == dt_id).filter(
            DtInletInfo.auth_status == constants.AUTH_STATUS_ACCEPT).first()
        if dt_inlet_info:
            change_data = json.loads(cut_record.record_json)
            update_payments = change_data.get('payment', {})
            if update_payments:
                self.close_dt_payments(dt_inlet_info.dt_id, update_payments)
        cut_record.status = INCUTTING
        # todo 更新支付缓存
        log.uline_dailycut.info('update dt info success, dt_id:{}'.format(dt_id))

    def close_dt_payments(self, dt_id, changed_payments):
        payments = self.uline_session.query(DtPayment).filter(DtPayment.dt_id == dt_id).all()
        db_payments = {each_payment.payment_type: each_payment for each_payment in payments}

        for pay_type in changed_payments:
            payment_info = changed_payments.get(pay_type, {})
            payment_type = int(payment_info.get('payment_type', 0))
            action_type = payment_info.get('action_type', 2)
            db_payment = db_payments.get(payment_type, None)
            update_rate = payment_info.get('update_payment_rate', None)
            if payment_type != int(pay_type):
                continue

            if action_type == 2 and db_payment:
                db_payment.update_at = self.current_time
                db_payment.daily_cut_status = 2

                exist_rate = db_payment.payment_rate
                if update_rate is None:
                    continue
                # 如果更新后的费率大于更新前的费率，则需要更新旗下商户的日切状态
                if exist_rate < update_rate:
                    sub_mch_query = self.uline_session.query(MchPayment.mch_id).join(MchInletInfo,
                                                                                     MchInletInfo.mch_id == MchPayment.mch_id)
                    sub_mch_query = sub_mch_query.join(DtPayment, and_(DtPayment.dt_id == MchInletInfo.dt_id,
                                                                       DtPayment.payment_type == MchPayment.payment_type))
                    sub_mch_query = sub_mch_query.filter(MchPayment.payment_rate < update_rate).filter(
                        DtPayment.dt_id == dt_id).filter(DtPayment.payment_type == int(payment_type))

                    self.uline_session.query(MchPayment).filter(
                        MchPayment.payment_type == int(payment_type)).filter(
                        MchPayment.mch_id.in_(sub_mch_query)).update({'daily_cut_status': 2},
                                                                     synchronize_session='fetch')

    def dt_daily_cut(self):
        now_time = datetime.now()
        cut_records = self.uline_session.query(DailyCutRecord).filter(
            DailyCutRecord.role_type == self.role_type).filter(
            DailyCutRecord.status == INCUTTING).all()
        for each_record in cut_records:
            update_datas = json.loads(each_record.record_json)
            with_draw_info = update_datas.get('withdraw', None)
            payments = update_datas.get('payment', None)
            dt_id = each_record.role_id
            print 'dt_daily_cut', dt_id
            if with_draw_info:
                # 修改数据
                db_withdraw_info = self.uline_session.query(D0WithdrawFee).filter(
                    D0WithdrawFee.role == dt_id).filter(
                    D0WithdrawFee.role_type == self.role_type).first()
                if db_withdraw_info:
                    for each_key in with_draw_info:
                        with_draw_value = with_draw_info.get(each_key, None)
                        setattr(db_withdraw_info, each_key, with_draw_value)
                        if with_draw_value is not None:
                            sub_mch_query = self.uline_session.query(D0WithdrawFee.role)
                            sub_mch_query = sub_mch_query.join(
                                MchInletInfo, MchInletInfo.mch_id == D0WithdrawFee.role)
                            sub_mch_query = sub_mch_query.filter(MchInletInfo.dt_id == dt_id)
                            sub_mch_query = sub_mch_query.filter(D0WithdrawFee.role_type == 'mch')
                            # 转换wx_draw_rate to wx
                            if each_key == 'wx_draw_rate':
                                each_key = 'wx'
                            elif each_key == 'ali_draw_rate':
                                each_key = 'alipay'
                            if each_key not in ['wx', 'alipay']:
                                continue
                            sub_mch_query = sub_mch_query.filter(getattr(D0WithdrawFee, each_key) != None)
                            sub_mch_query = sub_mch_query.filter(
                                getattr(D0WithdrawFee, each_key) < with_draw_value)
                            self.uline_session.query(D0WithdrawFee).filter(D0WithdrawFee.role_type == 'mch').filter(
                                D0WithdrawFee.role.in_(sub_mch_query)).update({each_key: with_draw_value},
                                                                              synchronize_session='fetch')
                else:
                    update_info = {
                        'update_at': self.current_time,
                        'role': dt_id,
                        'role_type': self.role_type,
                        'create_at': self.current_time
                    }
                    update_info.update(with_draw_info)
                    self.uline_session.add(D0WithdrawFee(**update_info))

            if payments:
                # 修改支付信息数据
                payments_list = self.uline_session.query(DtPayment).filter(DtPayment.dt_id == dt_id).all()
                db_payments = {}
                for payment in payments_list:
                    db_payments[payment.payment_type] = payment
                for each_type in payments:
                    update_payment_info = payments.get(each_type, None)
                    if not update_payment_info:
                        continue
                    action_type = update_payment_info.get('action_type', 2)
                    db_payment = db_payments.get(int(each_type), None)
                    if action_type == 2 and db_payment:
                        update_rate = update_payment_info.get('update_payment_rate', None)
                        exist_rate = db_payment.payment_rate
                        if update_rate is None:
                            continue
                        if exist_rate < update_rate:
                            sub_mch_query = self.uline_session.query(MchPayment.mch_id)
                            sub_mch_query = sub_mch_query.join(
                                MchInletInfo, MchInletInfo.mch_id == MchPayment.mch_id)
                            sub_mch_query = sub_mch_query.join(DtPayment,
                                                               and_(DtPayment.dt_id == MchInletInfo.dt_id,
                                                                    DtPayment.payment_type == MchPayment.payment_type))
                            sub_mch_query = sub_mch_query.filter(MchPayment.payment_rate < update_rate).filter(
                                DtPayment.dt_id == dt_id).filter(DtPayment.payment_type == int(each_type))

                            self.uline_session.query(MchPayment).filter(
                                MchPayment.payment_type == int(each_type)).filter(
                                MchPayment.mch_id.in_(sub_mch_query)).update(
                                {'payment_rate': update_rate, 'daily_cut_status': 1, 'settle_rate': update_rate},
                                synchronize_session='fetch')
                        db_payment.payment_rate = update_rate
                        # update_status = update_payment_info.get('pre_payment_status', None)
                        # if update_status:
                        #     db_payment.activated_status = update_status
                        db_payment.update_at = self.current_time
                        db_payment.daily_cut_status = 1

            if with_draw_info:
                # 修改数据
                db_withdraw_info = self.uline_session.query(D0WithdrawFee).filter(
                    D0WithdrawFee.role == dt_id).filter(
                    D0WithdrawFee.role_type == self.role_type).first()
                if db_withdraw_info:
                    for each_key in with_draw_info:
                        with_draw_value = with_draw_info.get(each_key, None)
                        setattr(db_withdraw_info, each_key, with_draw_value)
                        if with_draw_value is not None:
                            if each_key in ['wx_draw_fee', 'ali_draw_fee']:
                                each_key = 'wx' if each_key == 'wx_draw_fee' else 'alipay'
                            else:
                                continue
                            sub_mch_query = self.uline_session.query(D0WithdrawFee.role)
                            sub_mch_query = sub_mch_query.join(
                                MchInletInfo, MchInletInfo.mch_id == D0WithdrawFee.role)
                            sub_mch_query = sub_mch_query.filter(MchInletInfo.dt_id == dt_id)
                            sub_mch_query = sub_mch_query.filter(D0WithdrawFee.role_type == 'mch')
                            sub_mch_query = sub_mch_query.filter(getattr(D0WithdrawFee, each_key) != None)
                            sub_mch_query = sub_mch_query.filter(
                                getattr(D0WithdrawFee, each_key) < with_draw_value)
                            self.uline_session.query(D0WithdrawFee).filter(D0WithdrawFee.role_type == 'mch').filter(
                                D0WithdrawFee.role.in_(sub_mch_query)).update({each_key: with_draw_value},
                                                                              synchronize_session='fetch')
                else:
                    update_info = {
                        'update_at': self.current_time,
                        'role': dt_id,
                        'role_type': self.role_type,
                        'create_at': self.current_time
                    }
                    old_with_draw_info = {}
                    if with_draw_info.get('wx_draw_fee') or with_draw_info.get('wx'):
                        old_with_draw_info['wx'] = with_draw_info.get('wx_draw_fee') if with_draw_info.get(
                            'wx_draw_fee') else with_draw_info.get('wx')
                    if with_draw_info.get('ali_draw_fee') or with_draw_info.get('alipay'):
                        old_with_draw_info['alipay'] = with_draw_info.get('ali_draw_fee') if with_draw_info.get(
                            'ali_draw_fee') else with_draw_info.get('alipay')
                    update_info.update(old_with_draw_info)
                    self.uline_session.add(D0WithdrawFee(**update_info))

                db_payments = self.uline_session.query(DtPayment).filter(DtPayment.dt_id == dt_id).all()
                wx_withdraw = with_draw_info.get('wx') if with_draw_info.get(
                    'wx') else with_draw_info.get('wx_draw_fee')
                wx_draw_rate = with_draw_info.get('wx_draw_rate', None)
                alipay_withdraw = with_draw_info.get('alipay') if with_draw_info.get(
                    'alipay') else with_draw_info.get('ali_draw_fee')
                ali_draw_rate = with_draw_info.get('ali_draw_rate', None)
                for each_payment in db_payments:
                    # 写入手续费
                    if each_payment.uline_payment_id in ALI_PAY_TYPES:
                        if alipay_withdraw:
                            each_payment.withdraw_fee = alipay_withdraw
                        if ali_draw_rate:
                            each_payment.withdraw_rate = ali_draw_rate
                    elif each_payment.uline_payment_id in WX_PAY_TYPES:
                        if wx_withdraw:
                            each_payment.withdraw_fee = wx_withdraw
                        if wx_draw_rate:
                            each_payment.withdraw_rate = wx_draw_rate
                    self.uline_session.add(each_payment)

            each_record.status = CUTTED
            each_record.update_at = datetime.now()
            # 更新change_record状态
            change_record_id = update_datas.get('change_record_id', None)
            if change_record_id:
                change_record = self.uline_session.query(ChangeRecord).filter(
                    ChangeRecord.id == change_record_id).first()
                if change_record:
                    change_record.status = 2


def main():
    # test_add_change_record()
    is_debug = False
    if len(sys.argv) > 1:
        is_debug = sys.argv[1] == '1'

    initdb()
    current_time = datetime.now()
    cut_prepare_time = current_time.replace(hour=23, minute=55, second=0, microsecond=0)
    # 如果是非测试模式，则需要等到日切准备时间点
    if not is_debug and cut_prepare_time > current_time:
        log.uline_dailycut.info(
            'wait for preparing cutting time, {}, current time is {}'.format(cut_prepare_time, current_time))
        time.sleep((cut_prepare_time - current_time).total_seconds())

    close_paments(cut_prepare_time)

    clear_payment_cache()

    log.uline_dailycut.info('first clear payment cache')
    cut_time = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    if is_debug:
        cut_time = current_time + timedelta(minutes=1)

    current_time = datetime.now()
    log.uline_dailycut.info('current_time:{}'.format(current_time))
    log.uline_dailycut.info('cutting_time:{}'.format(cut_time))
    if current_time < cut_time:
        sleep_seconds = (cut_time - current_time).total_seconds()
        log.uline_dailycut.info('sleep seconds:{}'.format(sleep_seconds))
        if sleep_seconds > 0:
            log.uline_dailycut.info(
                'wait for cutting time, {}, current time is {}'.format(cut_time, current_time))
            # time.sleep(sleep_seconds)
    log.uline_dailycut.info('start cut, current time:{}'.format(datetime.now()))
    daily_cut(cut_prepare_time)
    update_all_diayly_cut_status()

    clear_payment_cache()


@catch_func_exception(0)
def update_all_diayly_cut_status():
    with uline_session_scope() as session:
        session.query(MchPayment).filter(MchPayment.daily_cut_status == 2).update({'daily_cut_status': 1},
                                                                                  synchronize_session='fetch')
        session.query(DtPayment).filter(DtPayment.daily_cut_status == 2).update({'daily_cut_status': 1},
                                                                                synchronize_session='fetch')


@catch_func_exception(5)
def close_paments(cut_prepare_time):
    current_time = datetime.now()
    with uline_session_scope() as session:
        mch_cut_util = PaymentsDailyCut(session, current_time, cut_prepare_time)
        dt_cut_util = DtDailycutUtil(session, current_time, cut_prepare_time)
        start_time = time.time()
        mch_cut_util.update_and_close_mch_payment_info()
        dt_cut_util.update_and_close_dt_mch_payment_info()
        end_time = time.time()
        log.uline_dailycut.info('close_payments time:{}s'.format(end_time - start_time))


@catch_func_exception(5)
def daily_cut(cut_prepare_time):
    current_time = datetime.now()
    with uline_session_scope() as session:
        mch_cut_util = PaymentsDailyCut(session, current_time, cut_prepare_time)
        dt_cut_util = DtDailycutUtil(session, current_time, cut_prepare_time)
        start_time = time.time()
        mch_cut_util.mch_daily_cut()
        dt_cut_util.dt_daily_cut()
        end_time = time.time()
        log.uline_dailycut.info('daily_cut time:{}s'.format(end_time - start_time))


@catch_func_exception(1)
def clear_payment_cache():
    http_client = HTTPClient()
    response = http_client.fetch(PAYMENT_CACHE_CLEAR_URL, method='GET')
    if response.body == 'success':
        return True


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(main)
