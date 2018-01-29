#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.public.constants import translate_payment_type
from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchPayment, DtPayment, MchInletInfo, D0WithdrawFee
from uline.model.uline.user import MchUser, DtUser
from tornado import ioloop


def update_dt_payment():
    dt_payments = uline_session.query(DtPayment, DtUser).join(DtUser, DtUser.dt_id == DtPayment.dt_id).all()
    uline_session.close()
    for dt_payment, dt_user in dt_payments:
        need_update = False
        tmp_str = translate_payment_type.get(dt_payment.payment_type)
        uline_payment_id, uline_settle_id, trade_type,\
            thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
        if not dt_payment.uline_payment_code:
            dt_payment.uline_payment_id = uline_payment_id
            dt_payment.uline_payment_code = uline_payment_code
            dt_payment.uline_settle_id = uline_settle_id
            dt_payment.trade_type = trade_type
            dt_payment.settle_rate = dt_payment.payment_rate
            need_update = True

        if not dt_payment.thirdparty_mch_id:
            # 微信千2
            if thirdparty_mch_id == '1' and dt_user.wx_sub_mch_id:
                new_thirdparty_mch_id = dt_user.wx_sub_mch_id
            # 微信千6
            elif thirdparty_mch_id == '2' and dt_user.wx_app_sub_mch_id:
                new_thirdparty_mch_id = dt_user.wx_app_sub_mch_id
            # 支付宝
            elif thirdparty_mch_id == '5' and dt_user.ali_sub_mch_id:
                new_thirdparty_mch_id = dt_user.ali_sub_mch_id
            else:
                new_thirdparty_mch_id = ''
            if new_thirdparty_mch_id != dt_payment.thirdparty_mch_id:
                dt_payment.thirdparty_mch_id = new_thirdparty_mch_id
                need_update = True

        if need_update:
            with uline_session_scope()as session:
                session.add(dt_payment)
                print('update dt_id:%s' % dt_payment.dt_id)

    return dt_payments


def update_mch_payment():
    # 目前浦发150万条数据
    for i in range(0, 150 * 10000, 10000):
        mch_payments = uline_session.query(MchPayment, MchInletInfo.dt_id, MchUser).\
            join(MchInletInfo, MchInletInfo.mch_id == MchPayment.mch_id).\
            join(MchUser, MchUser.mch_id == MchPayment.mch_id).\
            filter(MchPayment.uline_payment_code.is_(None)).\
            order_by('id').offset(i).limit(10000).all()
        if not mch_payments:
            break
    # mch_payments = uline_session.query(MchPayment,
    #                                    MchUser).\
    #     join(MchInletInfo, MchInletInfo.mch_id == MchPayment.mch_id).all()
            # MchPayment.uline_payment_code.isnot(None)).all()
        uline_session.close()
        for mch_payment, dt_id, mch_user in mch_payments:
            need_update = False
            tmp_str = translate_payment_type.get(mch_payment.payment_type)
            if not tmp_str:
                continue
            uline_payment_id, uline_settle_id, trade_type,\
                thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
            if not mch_payment.uline_payment_code:
                mch_payment.uline_payment_id = uline_payment_id
                mch_payment.uline_payment_code = uline_payment_code
                mch_payment.uline_settle_id = uline_settle_id
                mch_payment.trade_type = trade_type
                mch_payment.settle_rate = mch_payment.payment_rate
                need_update = True

            if not mch_payment.thirdparty_mch_id:
                # 微信千2
                if thirdparty_mch_id in ['1', '3', '4'] and mch_user.wx_sub_mch_id:
                    new_thirdparty_mch_id = mch_user.wx_sub_mch_id
                # 微信千6
                elif thirdparty_mch_id == '2' and mch_user.wx_app_sub_mch_id:
                    new_thirdparty_mch_id = mch_user.wx_app_sub_mch_id
                # 支付宝
                elif thirdparty_mch_id == '5' and mch_user.ali_sub_mch_id:
                    new_thirdparty_mch_id = mch_user.ali_sub_mch_id
                else:
                    new_thirdparty_mch_id = ''

                if new_thirdparty_mch_id != mch_payment.thirdparty_mch_id:
                    mch_payment.thirdparty_mch_id = new_thirdparty_mch_id
                    need_update = True

            if need_update:
                mch_payment.dt_id = dt_id
                with uline_session_scope()as session:
                    session.add(mch_payment)
                    print('update mch_id:%s' % mch_payment.mch_id)

    # return mch_payments


def update_dt_withdraw_fee():
    need_update_draw_rate = []
    dt_withdraw_fee = uline_session.query(DtPayment, D0WithdrawFee).\
        join(D0WithdrawFee, D0WithdrawFee.role == DtPayment.dt_id).filter(
            D0WithdrawFee.role_type == 'dt').all()
    uline_session.close()
    for dt_payment, withdraw_fee in dt_withdraw_fee:
        # 如果有d0费率，且withdraw_rate为空则更新
        if not dt_payment.withdraw_rate:
            if dt_payment.dt_id not in need_update_draw_rate:
                need_update_draw_rate.append(dt_payment.dt_id)

        if not dt_payment.withdraw_fee:
            # if 2:
            if dt_payment.payment_type in [7, 8, 9, 107, 108, 109]:
                new_withdraw_fee = withdraw_fee.alipay
            elif dt_payment.payment_type in [1, 2, 3, 4, 5, 11, 12, 13, 101, 102, 103, 104, 105]:
                new_withdraw_fee = withdraw_fee.wx
            else:
                continue
            if new_withdraw_fee != dt_payment.withdraw_fee:
                with uline_session_scope()as session:
                    dt_payment.withdraw_fee = new_withdraw_fee
                    session.add(dt_payment)
                    print('update withdraw_fee dt:%s' % dt_payment.dt_id)
    return need_update_draw_rate


def update_dt_withdraw_rate(dt_ids):
    for dt_id in dt_ids:
        ret = uline_session.query(DtPayment).filter(DtPayment.dt_id == dt_id).all()
        uline_session.close()
        wx_d1 = None
        wx_d0 = None
        wx_online_d1 = None
        wx_online_d0 = None
        ali_d1 = None
        ali_d0 = None
        # 获取支付宝、微信费率
        for row in ret:
            # 微信
            if row.payment_type in [101, 102, 103]:
                wx_d0 = row.payment_rate
            elif row.payment_type in [1, 2, 3]:
                wx_d1 = row.payment_rate
            # 微信
            elif row.payment_type in [4, 5]:
                wx_online_d1 = row.payment_rate
            elif row.payment_type in [104, 105]:
                wx_online_d0 = row.payment_rate
            # 支付宝
            elif row.payment_type in [7, 8, 9]:
                ali_d1 = row.payment_rate
            elif row.payment_type in [107, 108, 109]:
                ali_d0 = row.payment_rate
        # if wx_d1 and wx_d0:
        #     for row in ret:
        #         if row.payment_type in [1, 2, 3, 101, 102, 103] and not row.withdraw_rate and wx_d0 - wx_d1 >= 0:
        #             if row.withdraw_rate != wx_d0 - wx_d1:
        #                 new_withdraw_rate = wx_d0 - wx_d1
        #                 with uline_session_scope()as session:
        #                     row.withdraw_rate = new_withdraw_rate
        #                     session.add(row)
        #                     print('update wx withdraw_rate dt:%s' % row.dt_id)

        # if wx_online_d1 and wx_online_d0:
        #     for row in ret:
        #         if row.payment_type in [4, 5, 104, 105] and not row.withdraw_rate and wx_online_d0 - wx_online_d1 >= 0:
        #             if row.withdraw_rate != wx_online_d0 - wx_online_d1:
        #                 new_withdraw_rate = wx_online_d0 - wx_online_d1
        #                 with uline_session_scope()as session:
        #                     row.withdraw_rate = new_withdraw_rate
        #                     session.add(row)
        #                     print('update wx online withdraw_rate dt:%s' % row.dt_id)
        if ali_d1 and ali_d0:
            for row in ret:
                if row.payment_type in [7, 8, 9, 107, 108, 109] and not row.withdraw_rate and ali_d0 - ali_d1 >= 0:
                    if row.withdraw_rate != ali_d0 - ali_d1:
                        new_withdraw_rate = ali_d0 - ali_d1
                        with uline_session_scope()as session:
                            row.withdraw_rate = new_withdraw_rate
                            session.add(row)
                            print('update wx withdraw_rate dt:%s' % row.dt_id)


def update_mch_withdraw_rate(mch_ids):
    # 查询出渠道商的draw_rate
    for mch_id in mch_ids:
        ret = uline_session.query(DtPayment).\
            join(MchInletInfo, DtPayment.dt_id == MchInletInfo.dt_id).\
            join(MchPayment, MchPayment.mch_id == MchInletInfo.mch_id).\
            filter(MchPayment.mch_id == mch_id).all()
        # MchPayment.payment_type in (1, 2, 3, 4, 5, 101, 102, 103, 104, 105)).all()
        if not ret:
            continue
        uline_session.close()
        wx_d1_rate = None
        ali_d1_rate = None
        # 获取支付宝、微信费率
        for row in ret:
            # 微信
            if row.payment_type in [1, 2, 3, 4, 5, 101, 102, 103, 104, 105]:
                wx_d1_rate = row.withdraw_rate if row.withdraw_rate is not None else None
            # 支付宝
            elif row.payment_type in [7, 8, 9, 107, 108, 109]:
                ali_d1_rate = row.withdraw_rate if row.withdraw_rate is not None else None
        # if wx_d1_rate is not None:
        #     mch_paymnets = uline_session.query(MchPayment).filter(MchPayment.mch_id == mch_id).all()
        #     uline_session.close()
        #     for mch_paymnet in mch_paymnets:
        #         if mch_paymnet.payment_type in [1, 2, 3, 4, 5, 101, 102, 103, 104, 105] and not mch_paymnet.withdraw_rate:
        #             if mch_paymnet.withdraw_rate != wx_d1_rate:
        #                 with uline_session_scope()as session:
        #                     # 算出d1的费率
        #                     if mch_paymnet.payment_type > 100:
        #                         mch_paymnet.payment_type -= 100
        #                         mch_paymnet.payment_rate -= wx_d1_rate
        #                         mch_paymnet.settle_rate -= wx_d1_rate
        #                     mch_paymnet.withdraw_rate = wx_d1_rate
        #                     session.add(mch_paymnet)
        #                     print('update wx withdraw_rate mch:%s' % mch_paymnet.mch_id)
        if ali_d1_rate is not None:
            mch_paymnets = uline_session.query(MchPayment).filter(MchPayment.mch_id == mch_id).all()
            uline_session.close()
            for mch_paymnet in mch_paymnets:
                if mch_paymnet.payment_type in [7, 8, 9, 107, 108, 109] and not mch_paymnet.withdraw_rate:
                    if mch_paymnet.withdraw_rate != ali_d1_rate:
                        with uline_session_scope()as session:
                            # 算出d1的费率
                            if mch_paymnet.payment_type > 100:
                                mch_paymnet.payment_type -= 100
                                mch_paymnet.payment_rate -= ali_d1_rate
                                mch_paymnet.settle_rate -= ali_d1_rate
                            mch_paymnet.withdraw_rate = ali_d1_rate
                            session.add(mch_paymnet)
                            print('update wx withdraw_rate mch:%s' % mch_paymnet.mch_id)


def update_mch_withdraw_fee():
    need_update_draw_rate = []
    dt_withdraw_fee = uline_session.query(MchPayment, D0WithdrawFee).\
        join(D0WithdrawFee, D0WithdrawFee.role == MchPayment.mch_id).filter(
            D0WithdrawFee.role_type == 'mch').all()
    uline_session.close()
    fail = []
    success = 0
    for mch_payment, withdraw_fee in dt_withdraw_fee:
        try:
            if str(mch_payment.mch_id) in ['100002201127']:
                a = 1
            # 如果有d0费率，且withdraw_rate为空则更新
            if not mch_payment.withdraw_rate and mch_payment.payment_type > 100:
                if mch_payment.mch_id not in need_update_draw_rate:
                    need_update_draw_rate.append(mch_payment.mch_id)

            if not mch_payment.withdraw_fee:
                # if 2:
                if mch_payment.payment_type in [7, 8, 9, 107, 108, 109]:
                    new_withdraw_fee = withdraw_fee.alipay
                elif mch_payment.payment_type in [1, 2, 3, 4, 5, 11, 12, 13, 101, 102, 103, 104, 105]:
                    new_withdraw_fee = withdraw_fee.wx
                else:
                    continue
                # 如果D0WithdrawFee有记录，且不等于
                if new_withdraw_fee is not None and new_withdraw_fee != mch_payment.withdraw_fee:
                    with uline_session_scope()as session:
                        mch_payment.withdraw_fee = new_withdraw_fee
                        session.add(mch_payment)
                        print('update withdraw_fee mch:%s' % mch_payment.mch_id)
                        success += 1
                        print success
        except:
            # fail.append(mch_payment.mch_id)
            pass
    return need_update_draw_rate


def delete_dt_d0_payment():
    # 删除大于100的费率
    uline_session.query(DtPayment).filter(DtPayment.payment_type > 100).delete()
    dt_payments = uline_session.query(DtPayment).all()
    uline_session.close()
    # 如果有手续费和垫资费，则更改uline_settle_id为2
    for dt_payment in dt_payments:
        if dt_payment.withdraw_fee is not None or dt_payment.withdraw_rate is not None:
            if dt_payment.uline_settle_id != 2:
                dt_payment.uline_settle_id = 2
                with uline_session_scope()as session:
                    session.add(dt_payment)
                    print('update dt_id:%s' % dt_payment.dt_id)


def delete_mch_d0_payment():
    uline_session.query(MchPayment).filter(MchPayment.payment_type > 100).delete()


def main():
    # first
    # 转换渠道商dt_paymnet(将payment_type转成uline_paymnet_code)
    # update_dt_payment()
    # 转换商户mch_paymnet(将payment_type转成uline_paymnet_code)
    # update_mch_payment()

    # 更新渠道商提现手续费
    # need_update_dt_draw_rate = update_dt_withdraw_fee()
    # 更新渠道商垫资费
    # update_dt_withdraw_rate(need_update_dt_draw_rate)
    # 有部分渠道商需要手动处理下，比如有104没有4，大概有10个(默认给2，withdraw_fee有值，withdraw_rate为空)

    # second
    # 先保证渠道商的值都是对的
    # # 更新商户手续费
    need_update_mch_draw_rate = update_mch_withdraw_fee()
    # # # 更新商户垫资费
    update_mch_withdraw_rate(need_update_mch_draw_rate)

    # third
    # 删除渠道100以上费率
    delete_dt_d0_payment()
    # 删除商户100以上费率
    # delete_mch_d0_payment()
    pass

if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
