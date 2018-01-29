#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.public import constants
from uline.public.constants import old_payment_relations
from uline.settings import FEATURE_SWITCH
from uline.public.baseDB import DbClient
from uline.utils.dayzero.form_verify import get_update_changes, get_all_db_payments, get_new_all_db_payments

db = DbClient()


def check_mch_has_jd_pay(mch_id):
    """
    判断商户是否包含京东的费率，只要包含京东的费率，都不能手动审核
    :param mch_id:
    :return: True 代表这个商户包含京东或者审核通过以后包含D0的内容
    """

    # 如果平台没有开通京东支付，直接返回False
    if not FEATURE_SWITCH.get("JD_PAY"):
        return False

    with db.get_db() as cur:
        change_record = get_update_changes(cur, mch_id)
        changed_payments = change_record.get('payment', {})

        db_payments = get_new_all_db_payments(cur, mch_id)
        db_payments_paytypes = list()
        for each_payment in db_payments:
            db_payments_paytypes.append(each_payment[0])

        change_record = get_update_changes(cur, mch_id)

        changed_payments = change_record.get('payment', {})
        for payment_type in changed_payments:
            payment = changed_payments[payment_type]
            # 老的数字，转换成新的
            if str(payment.get('pay_type')).isdigit():
                payment_type = old_payment_relations.get((payment.get('pay_type')))
            action_type = payment.get('action_type', 2)
            if action_type == 1:
                db_payments_paytypes.append(payment_type)
            elif action_type == 2 and payment_type not in db_payments_paytypes:
                db_payments_paytypes.append(payment_type)
            elif action_type == 3 and payment_type in db_payments_paytypes:
                db_payments_paytypes.remove(payment_type)

        is_jd_mch = False
        for payment_type in db_payments_paytypes:
            if payment_type and (payment_type in constants.OFFLINE_D1_JD_PAY_TYPES or payment_type.endswith('_D0')):
                is_jd_mch = True

        return is_jd_mch
