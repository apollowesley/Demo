#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from decimal import Decimal
from wtforms import validators, fields, ValidationError, RadioField
from uline.public.baseDB import DbClient
import re
import json
from uline.public.constants import PAYMENT, PAY_CHANNEL, old_payment_relations
from uline.settings import FEATURE_SWITCH
from uline.public import constants

db = DbClient()


# 判断D0提现手续费符合不符合要求
def range_fee(form, field):
    father_id = None

    if not form.father_name:
        raise ValidationError(u'未获取到所属上级的名称')
    if form.father_name == 'dt':
        father_id = form.dt_id

    if not father_id:
        raise ValidationError(u'未获取到所属上级的编号')

    ret = db.selectSQL(
        "select wx, alipay from d0_withdraw_fee where role_type = %s and role = %s;",
        (form.father_name, father_id)
    )

    # 两个都为空，说明没有开通D0
    if not ret:
        raise ValidationError(u'上级未开通D0')

    else:
        # 方便阅读，转成字典
        ret = {'wx': ret[0], 'alipay': ret[1]}

        # 必须上级提现手续费不为空才可以设置下级的手续费
        if field.name == 'wx':
            if ret['wx'] is None:
                raise ValidationError(u'上级未开通微信的D0支付')
            else:
                if form.wx.data:
                    if form.wx.data < 0:
                        raise ValidationError(u'微信D0提现手续费不能小于0')

                    # 提现手续费不能小于上级设置的，只能大于或等于
                    if float(form.wx.data) * 100 < float(ret['wx']):
                        raise ValidationError(u'微信D0提现手续费不能小于上级设置的手续费')

        if field.name == 'alipay':
            if ret['alipay'] is None:
                raise ValidationError(u'上级未开通支付宝的D0支付')
            else:
                if form.alipay.data:
                    if form.alipay.data < 0:
                        raise ValidationError(u'支付宝D0提现手续费不能小于0')

                    if float(form.alipay.data) * 100 < float(ret['alipay']):
                        raise ValidationError(u'支付宝D0提现手续费不能小于上级设置的手续费')


# 判断商户的费率是不是符合条件，form表单验证
def validate_payment_rate(form, field):
    payment_type = re.search(r'(\d+)', field.name).groups()
    if not payment_type:
        # 为空说明前端页面没有按要求写dom元素的name
        raise ValidationError(u'费率类型错误')
    # 不为空就一定有第0个数据
    payment_type = int(payment_type[0])
    payment_name = PAYMENT[str(payment_type)]

    if not 2 <= field.data < 1000:
        raise ValidationError(u'{}的费率为2~1000'.format(
            payment_name))  # 1000为迎合网页需求

    payment_rate = db.selectSQL("""
        select payment_rate from dt_payment where dt_id=%s and payment_type=%s and activated_status in (1,2,3)
    """, (form.dt_id, payment_type))
    if payment_rate is None:
        raise ValidationError(u'渠道商没有设置{}的费率'.format(payment_name))
    else:
        if payment_type < 100 and (form.wx.data != None or form.alipay.data != None):
            raise ValidationError(u'商户D1和D0只能填写一种')
        if float(payment_rate[0]) > float(field.data) * 10:
            raise ValidationError(u'不能低于渠道商设置{}的费率'.format(payment_name))


def validate_one_payment_rate(payment_type, mch_rate, dt_id):
    """
    验证商户某一个费率是否符合条件，并返回响应的错误信息
    :param payment_type: 费率类型，1，2，3 104，109等等一类的
    :param mch_rate: 商户的费率，没有乘以10的时候
    :param dt_id: 渠道商的ID
    :return: 两个参数
        status: True 或 False, True 没有错误信息， False有错误信息
        error_message: "" 或 "详细的错误原因"
    """
    if not payment_type:
        return False, u'费率类型错误'

    payment_type = int(payment_type)

    d0 = False
    if payment_type > 100:
        if not FEATURE_SWITCH.get('OPEN_D0'):
            return False, u'平台未开通D0'

        # 如果新的进件，且 payment_type大于100
        if FEATURE_SWITCH.get('NEW_INLET') and payment_type > 100:
            d0 = True
            payment_type -= 100

    payment_name = PAYMENT[str(payment_type)]

    payment_rate = db.selectSQL("""
        select payment_rate, withdraw_rate from dt_payment where dt_id=%s and payment_type=%s and activated_status in (1,2,3)
    """, (dt_id, payment_type))
    if payment_rate is None:
        return False, u'渠道商没有设置{}的费率'.format(payment_name)
    else:
        if mch_rate:
            if float(payment_rate[0]) > float(mch_rate) * 10:
                return False, u'不能低于渠道商设置{}的费率'.format(payment_name)

        if FEATURE_SWITCH.get('NEW_INLET'):
            # 判断渠道商是否有设置垫资手续费
            if d0 and (payment_rate[1] is None):
                return False, u'渠道商没有设置{}的垫资手续费'.format(payment_name)
            # 如果是新的进件，且 payment_type大于100
            if d0 and float(payment_rate[0]) + float(payment_rate[1]) > float(mch_rate) * 10:
                return False, u'不能低于渠道商设置{}的费率'.format(payment_name)

    return True, ""


def verification_d0(selfobj):
    """
    验证D0相关设置的合法性
    :return: True 符合D0规则
    """
    wx_alipay = True
    if selfobj.wx:
        if not isinstance(selfobj.wx, Decimal):
            wx_alipay = False
            selfobj.form.errors['wx'] = [u'微信提现手续费异常']
        else:
            if not (
                selfobj.form.checkItem101.data >= 2 or
                selfobj.form.checkItem102.data >= 2 or
                selfobj.form.checkItem103.data >= 2
            ):
                wx_alipay = False
                selfobj.form.errors['checkItem'] = [u'微信D0费率必须大于等于2']

            if selfobj.form.checkItem104.data:
                if not selfobj.form.checkItem104.data >= 6:
                    wx_alipay = False
                    selfobj.form.errors['checkItem'] = [u'微信-D0－APP支付的费率设置错误, 需设置为大于等于6']
            if selfobj.form.checkItem105.data:
                if not selfobj.form.checkItem105.data >= 6:
                    wx_alipay = False
                    selfobj.form.errors['checkItem'] = [u'微信-D0－H5支付的费率设置错误, 需设置为大于等于6']
        if (
            selfobj.form.checkItem1 == 0 or
            selfobj.form.checkItem2 == 0 or
            selfobj.form.checkItem3 == 0
        ):
            wx_alipay = False
            selfobj.form.errors['checkItem'] = [u'0费率不能开通D0']

    if selfobj.alipay:
        if not isinstance(selfobj.alipay, Decimal):
            wx_alipay = False
            selfobj.form.errors['alipay'] = [u'支付宝提现手续费异常']
        else:
            if not (
                selfobj.form.checkItem107.data >= 2 or
                selfobj.form.checkItem108.data >= 2 or
                selfobj.form.checkItem109.data >= 2
            ):
                wx_alipay = False
                selfobj.form.errors['checkItem'] = [u'支付宝D0费率必须大于等于2']

            if (
                selfobj.form.checkItem7 == 0 or
                selfobj.form.checkItem8 == 0 or
                selfobj.form.checkItem9 == 0
            ):
                wx_alipay = False
                selfobj.form.errors['checkItem'] = [u'0费率不能开通D0']
    return wx_alipay


def check_d0_withdraw_fee(fee_value, dt_id, wx_or_ali):
    """
    检查D0提现手续费是否大于等于渠道商的提现手续费
    :param fee_value: 费率值
    :param dt_id: 渠道商ID
    :param wx_or_ali: weixin代表微信，alipay代表支付宝
    :return: True 代表符合条件 False 代表不符合条件
    """

    # 如果输入的都不是平台所支持的通道直接报错
    if wx_or_ali not in PAY_CHANNEL.keys():
        return False, u'程序错误，请联系渠道商'

    # 检查一下费率本身是否包含非法字符
    if check_fee_is_correct(fee_value):

        fee_value = float(fee_value)

        ret = db.selectSQL(
            "select wx, alipay from d0_withdraw_fee where role_type = %s and role = %s;",
            ('dt', dt_id)
        )

        if ret is None:
            return False, u'渠道商没有开通D0'

        # 方便阅读，转成字典
        ret = {'weixin': ret[0], 'alipay': ret[1]}

        # 必须渠道商提现手续费不为空才可以设置下级的手续费
        if ret[wx_or_ali] is None:
            return False, u'渠道商未开通{0}D0支付'.format(PAY_CHANNEL.get(wx_or_ali))
        else:
            # 提现手续费不能小于渠道商设置的，只能大于或等于
            if fee_value < (ret[wx_or_ali] / 100):
                return False, u'{0}D0提现手续费不能小于渠道商设置的手续费'.format(PAY_CHANNEL.get(wx_or_ali))
            else:
                return True, ""
    else:
        return False, u'{0}D0提现手续费包含非法字符'.format(PAY_CHANNEL.get(wx_or_ali))


def check_fee_is_correct(fee_value):
    """
    判断各种提现手续费或者其他类型的字符串，是不是int或float，并且判断是不是为空
    :param fee_value: str类型的费率
    :return: True代表符合要求，False代表为空或者不是int和float
    """
    # 不为None
    if fee_value is not None:
        fee_value = str(fee_value)
        return fee_value.replace('.', '', 1).isdigit()
    else:
        return False


def get_update_changes(cur, mch_id):
    """
    获取商户修改中的内容
    :param cur:
    :param mch_id:
    :return:
    """
    sql = """select data_json from change_record where mch_id=%s and status=1;"""
    cur.execute(sql, (mch_id,))
    query_change_record_json = cur.fetchone()
    # 验证数据的合法性
    if query_change_record_json:
        query_change_record = json.loads(query_change_record_json[0])
        if isinstance(query_change_record, dict):
            return query_change_record
    else:
        return {}


def get_all_db_payments(cursor, mch_id):
    """
    获取商户现有的费率
    :param cursor:
    :param mch_id:
    :return:
    """
    query = """select payment_type from mch_payment where mch_id=%s"""
    cursor.execute(query, (mch_id,))
    return cursor.fetchall()


def get_new_all_db_payments(cursor, mch_id):
    """
    获取商户现有的费率
    :param cursor:
    :param mch_id:
    :return:
    """
    query = """select uline_payment_code from mch_payment where mch_id=%s"""
    cursor.execute(query, (mch_id,))
    return cursor.fetchall()


def get_all_db_roles(cursor, mch_id):
    """
    获取商户现有的费率
    :param cursor:
    :param mch_id:
    :return:
    """
    query = """select withdraw_fee, withdraw_rate from mch_payment where mch_id=%s"""
    cursor.execute(query, (mch_id,))
    return cursor.fetchall()


def check_mch_is_d0(mch_id):
    """
    判断商户是否包含D0的费率，只要包含D0的费率，都不能手动激活
    :param mch_id:
    :return: True 代表这个商户包含D0或者审核通过以后包含D0的内容
    """

    # 如果平台没有开通D0，直接返回False
    if not FEATURE_SWITCH.get("OPEN_D0"):
        return False

    with db.get_db() as cur:
        change_record = get_update_changes(cur, mch_id)

        # db_payments = get_all_db_payments(cur, mch_id)
        db_payments = get_new_all_db_payments(cur, mch_id)
        db_roles = get_all_db_roles(cur, mch_id)
        db_payments_paytypes = list()
        for each_payment in db_payments:
            db_payments_paytypes.append(each_payment[0])

        change_record = get_update_changes(cur, mch_id)

        changed_payments = change_record.get('payment', {})
        changed_roles = change_record.get('role', {})
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

        is_d0_mch = False
        for payment_type in db_payments_paytypes:
            if payment_type and (payment_type in constants.D0_PAY_TYPES or payment_type.endswith('_D0')):
                is_d0_mch = True

        # 判断是否包含手续费
        if not is_d0_mch:
            for role in db_roles:
                if role and (role[0] or role[1]):
                    is_d0_mch = True
        # 判断是否新增role
        if not is_d0_mch and changed_roles:
            if changed_roles.get('wx') or changed_roles.get('alipay') \
                    or changed_roles.get('wx_draw_fee') or changed_roles.get('ali_draw_fee'):
                is_d0_mch = True

        return is_d0_mch
