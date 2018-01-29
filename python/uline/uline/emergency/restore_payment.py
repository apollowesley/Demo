#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from uline.public.constants import AVAILABLE_PAYMENTS_FORMAT, translate_payment_type, new_payment_relations, \
    old_payment_relations
# from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchPayment, DtPayment, MchInletInfo, D0WithdrawFee
from uline.model.uline.user import MchUser
from uline.model.uline.other import ChangeRecord
from tornado import ioloop


from uline.model.uline.base import Model as uline_Model, uline_Session
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

# sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@192.168.20.100:5432/spd_uline'
sqlalchemy_uline_db = 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@127.0.0.1:16691/spd_uline'
# sqlalchemy_uline_db = 'postgresql+psycopg2://uline:uline2015@127.0.0.1:7890/uline'


def initdb():
    uline_engine = create_engine(sqlalchemy_uline_db, echo=False)
    uline_Session.configure(bind=uline_engine)
    uline_Model.metadata.bind = uline_engine


@contextmanager
def uline_session_scope():
    session = uline_Session()
    try:
        yield session
        print 'session commit'
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_change_rocord():
    # change_records = uline_session.query(ChangeRecord).filter(ChangeRecord.create_at > '2017-10-31', ChangeRecord.mch_id == '100009984269').all()
    change_records = uline_session.query(ChangeRecord).filter(ChangeRecord.create_at > '2017-10-31').all()
    uline_session.close()
    for temp in change_records:
        # {"license_scope": "", "role":
        # {"wx_draw_rate": "2", "wx_draw_fee": "50"},
        # "payment":
        # {"WX_OFFLINE_NATIVE": {"pay_type": "WX_OFFLINE_NATIVE", "after_auth_status": 2, "activated_status": 3, "pay_rate": 38, "action_type": 2, "settle_rate": 38, "pre_status": 2},
        #  "WX_OFFLINE_MICROPAY": {"pay_type": "WX_OFFLINE_MICROPAY", "after_auth_status": 2, "activated_status": 3, "pay_rate": 38, "action_type": 2, "settle_rate": 38, "pre_status": 2},
        # "WX_OFFLINE_JSAPI": {"pay_type": "WX_OFFLINE_JSAPI", "after_auth_status": 2, "activated_status": 3, "pay_rate": 38, "action_type": 2, "settle_rate": 38, "pre_status": 2}}, "pre_auth_status": 2,
        # "balance_info": {"update_at": "2017-11-06"}}

        data_json = json.loads(temp.data_json)
        payments = data_json.get('payment')
        role = data_json.get('role')

        # 如果存在修改费率，判断mch_paymnet表中是否有
        if payments:
            mcn_payment = uline_session.query(MchPayment).filter(MchPayment.mch_id == temp.mch_id).all()
            uline_session.close()
            if not mcn_payment:
                try:
                    dt_id = uline_session.query(MchInletInfo.dt_id).filter(
                        MchInletInfo.mch_id == temp.mch_id).first()[0]
                    uline_session.close()
                except:
                    continue
                wx_sub_mch_id = uline_session.query(MchUser.wx_sub_mch_id).filter(
                    MchUser.mch_id == temp.mch_id).first()[0]
                uline_session.close()

                wx_app_sub_mch_id = uline_session.query(MchUser.wx_app_sub_mch_id).filter(
                    MchUser.mch_id == temp.mch_id).first()[0]
                uline_session.close()

                ali_sub_mch_id = uline_session.query(MchUser.ali_sub_mch_id).filter(
                    MchUser.mch_id == temp.mch_id).first()[0]
                uline_session.close()

                for key in AVAILABLE_PAYMENTS_FORMAT.keys() + old_payment_relations.keys():
                    single_payment = payments.get(key)
                    if single_payment:
                        # 有可能是老版本数字
                        try:
                            # new_key = int(key)
                            # if new_key > 100:
                            #     old_payment_type = new_key - 100
                            # else:
                            old_payment_type = int(key)
                        except:
                            old_payment_type = int(new_payment_relations.get(key))
                        tmp_str = translate_payment_type.get(old_payment_type)
                        uline_payment_id, uline_settle_id, trade_type,\
                            thirdparty_mch_id, uline_payment_code = tmp_str.split('|')

                        new_mch_payment = {
                            'mch_id': temp.mch_id,
                            'dt_id': dt_id,

                            'uline_payment_id': uline_payment_id,
                            'uline_payment_code': uline_payment_code,
                            'uline_settle_id': uline_settle_id,
                            'trade_type': trade_type,


                            'settle_rate': single_payment.get('pay_rate'),

                            'payment_rate': single_payment.get('pay_rate'),
                            'payment_type': old_payment_type,

                            'activated_status': 2,
                        }

                        if old_payment_type in [1, 2, 3, 101, 102, 103]:
                            new_mch_payment['thirdparty_mch_id'] = wx_sub_mch_id
                        if old_payment_type in [4, 5, 104, 105]:
                            new_mch_payment['thirdparty_mch_id'] = wx_app_sub_mch_id
                        if old_payment_type in [7, 8, 9, 107, 108, 109]:
                            new_mch_payment['thirdparty_mch_id'] = ali_sub_mch_id
                        if role:
                            if role.get('wx_draw_fee') or role.get('ali_draw_fee'):
                                new_mch_payment['withdraw_fee'] = role.get('wx_draw_fee') if role.get(
                                    'wx_draw_fee') else role.get('ali_draw_fee')
                                new_mch_payment['withdraw_rate'] = role.get('wx_draw_rate') if role.get(
                                    'wx_draw_rate') else role.get('ali_draw_rate')
                            if role.get('wx') or role.get('alipay'):
                                new_mch_payment['withdraw_fee'] = role.get(
                                    'wx') if role.get('wx') else role.get('alipay')
                                # 查询渠道商垫资费
                                wx_d1_rate = None
                                ali_d1_rate = None
                                # 获取支付宝、微信费率
                                ret = uline_session.query(DtPayment).filter(DtPayment.dt_id == dt_id).all()
                                uline_session.close()
                                for row in ret:
                                    # 微信
                                    if row.payment_type in [1, 2, 3, 4, 5, 101, 102, 103, 104, 105]:
                                        wx_d1_rate = row.withdraw_rate if row.withdraw_rate is not None else None
                                    # 支付宝
                                    elif row.payment_type in [7, 8, 9, 107, 108, 109]:
                                        ali_d1_rate = row.withdraw_rate if row.withdraw_rate is not None else None
                                if role.get('wx'):
                                    new_mch_payment['withdraw_rate'] = wx_d1_rate
                                else:
                                    new_mch_payment['withdraw_rate'] = ali_d1_rate
                        with uline_session_scope()as session:
                            _new_mch_payment = MchPayment(**new_mch_payment)
                            session.add(_new_mch_payment)
                            print('create mch_id:%s' % _new_mch_payment.mch_id)
                # {"license_img": "3b4f51be468f490798dc48bad57be026.jpg", "annex_img1": "4e712352da1b4c548e731d1fcf5e4518.jpg", "annex_img2": "e20472ed5062406b858e7373da1914fc.jpg", "annex_img3": "069c77f2defe42c7b74a5844b46842ec.jpg", "balance_info": {"update_at": "2017-10-31"}, "role": {"alipay": 50, "action_type": 1, "wx": 50}, "pre_auth_status": 2, "id_card_img_b": "c932e3409cde435daff63e63f9e15d82.jpg", "payment": {"1": {"pay_type": 1, "pay_rate": 28, "activated_status": 2, "pre_status": 2, "action_type": 3}, "2": {"pay_type": 2, "pay_rate": 28, "activated_status": 2, "pre_status": 2, "action_type": 3}, "3": {"pay_type": 3, "pay_rate": 28, "activated_status": 2, "pre_status": 2, "action_type": 3}, "7": {"pay_type": 7, "pay_rate": 28, "activated_status": 2, "pre_status": 2, "action_type": 3}, "8": {"pay_type": 8, "pay_rate": 28, "activated_status": 2, "pre_status": 2, "action_type": 3}, "9": {"pay_type": 9, "pay_rate": 28, "activated_status": 2, "pre_status": 2, "action_type": 3}, "102": {"pay_type": "102", "after_auth_status": 2, "activated_status": 1, "pay_rate": 30, "action_type": 1, "pre_status": 1}, "103": {"pay_type": "103", "after_auth_status": 2, "activated_status": 1, "pay_rate": 30, "action_type": 1, "pre_status": 1}, "101": {"pay_type": "101", "after_auth_status": 2, "activated_status": 1, "pay_rate": 30, "action_type": 1, "pre_status": 1}}, "id_card_img_f": "41d52f8873c443679d3013198de0d4c8.jpg"}
                # 保存到mch_payment表中


def main():
    get_change_rocord()
    pass


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
