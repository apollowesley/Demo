#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.public.constants import translate_payment_type
from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchPayment, DtPayment, MchInletInfo, D0WithdrawFee
from uline.model.uline.user import MchUser, DtUser
from tornado import ioloop


def update_mch_sub_id():
    results = uline_session.query(MchPayment, MchUser).\
        join(MchUser, MchPayment.mch_id == MchUser.mch_id).filter(
        MchUser.wx_sub_mch_id.isnot(None), MchPayment.thirdparty_mch_id == '',
        MchPayment.payment_type.in_(['1', '2', '3'])).all()
    uline_session.close()
    for mch_payment, mch_user in results:
        need_update = False
        if mch_user.wx_sub_mch_id:
            mch_payment.thirdparty_mch_id = mch_user.wx_sub_mch_id
            need_update = True
        if need_update:
            with uline_session_scope()as session:
                session.add(mch_payment)
                print('update sub_mch mch_id:%s' % mch_payment.mch_id)

    return results


def update_mch_app_sub_id():
    results = uline_session.query(MchPayment, MchUser).\
        join(MchUser, MchPayment.mch_id == MchUser.mch_id).filter(
        MchUser.wx_app_sub_mch_id.isnot(None), MchPayment.thirdparty_mch_id == '',
        MchPayment.payment_type.in_(['4', '5'])).all()
    uline_session.close()
    for mch_payment, mch_user in results:
        need_update = False
        if mch_user.wx_sub_mch_id:
            mch_payment.thirdparty_mch_id = mch_user.wx_app_sub_mch_id
            need_update = True
        if need_update:
            with uline_session_scope()as session:
                session.add(mch_payment)
                print('update app_sub_mch mch_id:%s' % mch_payment.mch_id)

    return results


def update_mch_ali_sub_id():
    results = uline_session.query(MchPayment, MchUser).\
        join(MchUser, MchPayment.mch_id == MchUser.mch_id).filter(
        MchUser.ali_sub_mch_id.isnot(None), MchPayment.thirdparty_mch_id == '',
        MchPayment.payment_type.in_(['7', '8', '9'])).all()
    uline_session.close()
    for mch_payment, mch_user in results:
        need_update = False
        if mch_user.wx_sub_mch_id:
            mch_payment.thirdparty_mch_id = mch_user.ali_sub_mch_id
            need_update = True
        if need_update:
            with uline_session_scope()as session:
                session.add(mch_payment)
                print('update alipay_mch mch_id:%s' % mch_payment.mch_id)

    return results


def main():
    update_mch_sub_id()
    update_mch_app_sub_id()
    update_mch_ali_sub_id()

if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
