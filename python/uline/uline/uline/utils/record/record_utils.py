# -*- coding: utf-8 -*-
from __future__ import division

import json
import os

from tornado import gen
from uline.public.constants import old_payment_relations
from uline.model.uline.user import BkUser
from uline.model.uline.base import uline_session
from uline.public.db import initdb
from uline.model.uline.info import BalanceBankInfo
from uline.public.db import uline_session_scope
from uline.public import constants


@gen.coroutine
def update_result(self_obj, result, keys, change_id, change_type=2):
    """用change_record里面的新的修改替换result里面的值
    :param self_obj: handler 类对象，获取特定的属性
    :param result: select 语句返回的结果
    :param keys:  select 语句查询的字段
    :param change_id: mch_id 或 dt_id
    :param change_type: 是渠道商还是商户1为渠道商,2为商户
    :return: 更新后的结果
    """
    changes_record = yield select_change_record(self_obj, change_id, change_type=change_type)
    if result and changes_record:
        # 原来的值是tuple不支持修改，所以先转换为list
        result = list(result)
        changes = json.loads(changes_record[1])
        for index, key in enumerate(keys):
            # 如果change_record有对应值， 就优先使用change_record里面的值
            result[index] = changes.get(key) or result[index]
        result = tuple(result)
    raise gen.Return(result)


@gen.coroutine
def select_change_record(self_obj, obj_id, change_type=1, status=(1, 4)):
    """
        负责查询change_record表有没有一个渠道商，拥有一条正在审核中的记录
        :param self_obj: 类的对象，需要访问操作类的一些方法和属性
        :param dt_id: 渠道商的ID
        :return: 返回的是查询的结果
        """
    if change_type == 1:

        query = """
            select dt_id, data_json,id from change_record
             where change_type = 1 and status in %s and dt_id = %s order by id DESC;
        """

        # 查询有没有对应的记录
        raise gen.Return(self_obj.db.selectSQL(query, (status, obj_id)))
    elif change_type == 2:
        query = """
                    select mch_id, data_json from change_record
                     where change_type = 2 and status in %s and mch_id = %s order by id DESC;
                """

        # 查询有没有对应的记录
        raise gen.Return(self_obj.db.selectSQL(query, (status, obj_id)))


@gen.coroutine
def select_change_record_by_dt_id(self_obj, fetchone=True, change_type=1):
    """
        根据渠道商的ID来查询，是不是已经有该渠道商的记录了
        :return: 返回查询结果
    """

    if change_type == 1:
        query = """select id from change_record where dt_id = %s and status=1;"""
        raise gen.Return(self_obj.db.selectSQL(query, (self_obj.dt_id,), fetchone=fetchone))
    elif change_type == 2:
        query = """select id from change_record where mch_id = %s and status=1;"""
        raise gen.Return(self_obj.db.selectSQL(query, (self_obj.mch_id,), fetchone=fetchone))
    elif change_type == 3:
        query = """select id from change_record where dt_id = %s and status=1;"""
        raise gen.Return(self_obj.db.selectSQL(query, (self_obj.chain_id,), fetchone=fetchone))


@gen.coroutine
def update_change_record_status(self_obj, status=3, change_type=1):
    if change_type == 1:
        query = """
            update change_record set status = %s, create_at = now() where dt_id = %s and status=1;
        """
        raise gen.Return(self_obj.db.executeSQL(query, (status, self_obj.dt_id,)))
    elif change_type == 2:
        query = """
            update change_record set status = %s, create_at = now() where mch_id = %s and status=1;
        """
        raise gen.Return(self_obj.db.executeSQL(query, (status, self_obj.mch_id,)))


@gen.coroutine
def rollback(self_obj, change_type=1, cursor=None):
    query = ""
    search_id = 0
    if change_type == 1:
        # 先更新状态为驳回
        search_id = self_obj.dt_id
        query = """
            update dt_payment set activated_status = %s where dt_id = %s and payment_type = %s;
        """

    elif change_type == 2:
        # 先更新状态为驳回
        search_id = self_obj.mch_id
        query = """
                    update mch_payment set activated_status = %s where mch_id = %s and payment_type = %s;
                """

    change_info = yield select_change_record(self_obj, search_id, change_type=change_type)
    if not change_info:
        raise gen.Return(True)
    result = json.loads(change_info[1]).get('payment', dict())
    payments = {}
    # 兼容以前列表数据
    if isinstance(result, list):
        for each_payment in result:
            payment_info = dict()
            payment_info['pay_type'] = each_payment[0]
            payment_info['pre_status'] = each_payment[2]
            payments[each_payment[0]] = payment_info
    elif isinstance(result, dict):
        payments = result
    for payment_type in payments:
        payment = payments[payment_type]
        if 'action_type' not in payment:
            self_obj.db.executeSQL(query, (payment['pre_status'], search_id, payment_type))
    update_change_record_status(self_obj, change_type=change_type)
    raise gen.Return(True)


def update_change_record(self_obj, args_tuple, change_type=1):
    if change_type == 1:
        query = """
            update change_record set data_json=%s, change_type=1, status=%s, create_at=now()
             where dt_id = %s and status=1;
        """
        self_obj.db.executeSQL(query, args_tuple)
    elif change_type == 2:
        query = """
            update change_record set data_json=%s, change_type=2, status=%s, create_at=now()
             where mch_id = %s and status=1;
        """
        self_obj.db.executeSQL(query, args_tuple)


def insert_change_record(self_obj, args_tuple, change_type=1):
    query = ''

    # 渠道商相关
    if change_type == 1:
        query = """
            insert into change_record(dt_id, data_json, change_type, status, create_at)
             values(%s, %s, 1, 1, now());
        """
    # 商户相关
    elif change_type == 2:
        query = """
            insert into change_record(mch_id, data_json, change_type, status, create_at)
             values(%s, %s, 2, 1, now());
        """
    self_obj.db.executeSQL(query, args_tuple)


# 把原来要显示给用户的费率，替换成用户新修改的费率
def swap_value(update_info, data, change_id='', role_type=1):
    if not isinstance(data, dict):
        raise Exception('数据类型错误')
    is_authed = data.get('auth_status', 1) == constants.AUTH_STATUS_ACCEPT
    if update_info:
        if 'role' in update_info:
            should_change_role = update_info.get('role')
            # 替换提现手续费(兼容老的wx)
            if should_change_role.get('wx'):
                should_change_role['wx_draw_fee'] = should_change_role.get('wx')
                should_change_role.pop('wx')
            if should_change_role.get('alipay'):
                should_change_role['ali_draw_fee'] = should_change_role.get('alipay')
                should_change_role.pop('alipay')
            # if isinstance(should_change_role.get('wx_draw_fee'), int):
            if should_change_role.get('wx_draw_fee'):
                try:
                    should_change_role['wx_draw_fee'] = int(should_change_role['wx_draw_fee']) / 100
                except ValueError:
                    should_change_role.pop('wx_draw_fee')

            # if isinstance(should_change_role.get('ali_draw_fee'), int):
            if should_change_role.get('ali_draw_fee'):
                try:
                    should_change_role['ali_draw_fee'] = int(should_change_role['ali_draw_fee']) / 100
                except ValueError:
                    should_change_role.pop('ali_draw_fee')
            # 替换垫资费
            # if isinstance(should_change_role.get('wx_draw_rate'), int):
            if should_change_role.get('wx_draw_rate'):
                try:
                    should_change_role['wx_draw_rate'] = int(should_change_role['wx_draw_rate']) / 10.0
                except ValueError:
                    should_change_role.pop('wx_draw_rate')
            if should_change_role.get('ali_draw_rate'):
                try:
                    should_change_role['ali_draw_rate'] = int(should_change_role['ali_draw_rate']) / 10.0
                except ValueError:
                    should_change_role.pop('ali_draw_rate')

            if should_change_role:
                update_info.update(should_change_role)

        if 'del_annex' in update_info:
            del_annex = str(update_info.get('del_annex'))
            if del_annex:
                for annex_count in del_annex.split("-"):
                    update_info["annex_img" + annex_count] = None

        if 'del_wx_dine_annex' in update_info:
            del_wx_dine_annex = update_info.get('del_wx_dine_annex', [])
            for annex_count in del_wx_dine_annex:
                update_info['wx_dine_annex_img' + str(annex_count)] = None

        if update_info.get('payment', {}):
            # 需要更新的数据
            should_change_payments = update_info.get('payment')
            # 如果有payment字段，且是list类型的，就是最早的数据结构
            changed_payments = dict()
            if isinstance(should_change_payments, list):
                for each_payment in should_change_payments:
                    changed_payments[int(each_payment[0])] = {
                        'pay_type': each_payment[0], 'pay_rate': each_payment[1] / 10.0}

            else:
                new_change_payments = {}
                for each_paytype in should_change_payments:
                    # 老版本使用数字
                    if not str(each_paytype).isdigit():
                        new_each_paytype = constants.new_payment_relations.get(str(each_paytype))
                        pay_info = should_change_payments[each_paytype]
                    else:
                        new_each_paytype = each_paytype
                        pay_info = should_change_payments[each_paytype]
                    pay_info['pay_rate'] = pay_info['pay_rate'] / 10.0
                    pay_info['pay_type'] = new_each_paytype
                    new_change_payments[new_each_paytype] = pay_info
                changed_payments = new_change_payments

            # 从数据库中获取的数据
            db_payments = data.get('payment', {})
            db_payments = {each_payment.get('pay_type'): each_payment for each_payment in db_payments}
            # db_payments = {each_payment.get('uline_payment_code'): each_payment for each_payment in db_payments}
            # db_payment_types = set(db_payments.keys())
            # changed_payment_types = set(db)

            # 首先获取在change_record中的支付方式
            only_db_payments = [pay_type for pay_type in db_payments if pay_type not in changed_payments]

            only_change_payments = [pay_type for pay_type in changed_payments if pay_type not in db_payments]

            all_type_payments = [pay_type for pay_type in db_payments if pay_type in changed_payments]

            payments = {}
            # 只有数据库中包含
            for pay_type in only_db_payments:
                if pay_type:
                    payments[pay_type] = db_payments[pay_type]

            # 只存在change_record中
            for pay_type in only_change_payments:
                # 就是新增
                payment_info = changed_payments[pay_type]
                if payment_info.get('action_type', 3) == 1:
                    payment_info['operate'] = 0
                    payments[pay_type] = payment_info

            for pay_type in all_type_payments:
                db_payment = db_payments[pay_type]
                # 如果不存在uline_payment_code，则添加
                if not db_payment.get('uline_payment_code'):
                    uline_payment_code = old_payment_relations.get(str(pay_type))
                    if uline_payment_code:
                        db_payment['uline_payment_code'] = uline_payment_code
                db_payment['operate'] = 1
                change_payment = changed_payments[pay_type]
                action_type = change_payment.get('action_type', 2)

                # 是审核通过后，就可以进行修改
                if not is_authed:
                    db_payment['operate'] = 0
                if action_type == 2:
                    # 如果是更新，就直接使用change_record中的数据覆盖原有的
                    current_status = db_payment['activated_status']
                    db_payment.update(change_payment)
                    if is_authed:
                        db_payment['activated_status'] = current_status
                    payments[pay_type] = db_payment
                elif action_type == 1:
                    payments[pay_type] = db_payment

#             try:
                # paymnet_value = payments.values()
                # for single in paymnet_value:
                    # # 旧版的payment_type
                    # # if isinstance(single.get('pay_type'), int):
                    # #     raise
                    # if single.get('pay_rate') is not None:
                    # single['settle_rate'] = single.get('pay_rate')
                    # # 判断pay_type是否为数字（老的）
                    # if isinstance(single.get('pay_type'), int):
                    # single['pay_type'] = old_payment_relations.get(str(single.get('pay_type')))
                    # single['uline_payment_code'] = single.get('pay_type')
                    # if single.get('uline_payment_code').endswith('D0'):
                    # single['uline_settle_id'] = 2
                    # else:
                    # single['uline_settle_id'] = 1
                    # else:
                    # paymnet_value.remove(single)
                # paymnet_value.sort(key=lambda x: (x.get('uline_settle_id'),
                    # x.get('uline_payment_code')), reverse=True)
                # data['payment'] = paymnet_value
            # except:
                # raise
            data['payment'] = sorted(payments.values(), key=lambda payment: payment['pay_type'])
            for singe_payment in data.get('payment'):
                uline_payment_code = singe_payment.get('uline_payment_code')
                settle_rate = singe_payment.get('settle_rate')
                pay_rate = singe_payment.get('pay_rate')
                if not uline_payment_code:
                    singe_payment['uline_payment_code'] = old_payment_relations.get(
                        str(singe_payment.get('pay_type')))
                # 已pay_rate为准
                if pay_rate and settle_rate and pay_rate != settle_rate:
                    singe_payment['settle_rate'] = singe_payment.get('pay_rate')
                if not settle_rate:
                    singe_payment['settle_rate'] = singe_payment.get('pay_rate')
        if change_id:
            # 需要先对图片地址进行修正
            _format_record_imgs(update_info, change_id, role_type)

        # 结算账户信息
        if 'balance_info' in update_info:
            balance_info = update_info['balance_info']
            update_info.update(balance_info)
            # 银行名称获取
            if 'bank_no' in balance_info:
                initdb()
                with uline_session_scope() as session:
                    bank_name = get_balance_bank_name(session, balance_info['bank_no'])
                    if bank_name:
                        update_info['bank_name'] = bank_name
            del update_info['balance_info']

        # if 'bk_id' in update_info:
        #     # 获取bk_type
        #     bk_profile = uline_session.query(BkUser).filter(BkUser.bk_id == update_info["bk_id"]).one()
        #     update_info['bk_type'] = bk_profile.bk_type
        #     update_info['bk_name'] = bk_profile.bk_name
        deep_update_dict_values(data, update_info, except_keys=['payment'])
    return data


def get_balance_bank_name(session, bank_no):
    """
    获取银行支行名
    """
    if bank_no:
        balance_info = session.query(BalanceBankInfo).filter(BalanceBankInfo.bank_no == bank_no).first()
        if balance_info:
            return balance_info.bank_name


def _format_record_imgs(inlet_infos, change_id, role_type=1):
    """修改记录中图片路径矫正.
        Args:
            change_id: 商户号或渠道号.
            role_type: 1为渠道商信息，2为商户信息
    """
    base_dir = '/static/uploads/dt/idcard' if role_type == 1 else '/static/uploads/mch/idcard'
    file_dir = os.path.join(base_dir, '{}'.format(change_id))
    each_dict = ['id_card_img_b', 'id_card_img_f', 'license_img',
                 'mch_desk_img', 'mch_inner_img', 'mch_front_img'
                 'img_with_id_card', 'mch_desk_img', 'mch_inner_img', 'mch_front_img']
    each_dict += ['annex_img' + str(i) for i in range(1, 6)]
    each_dict += ['wx_dine_annex_img' + str(i) for i in range(1, 6)]
    for each_key in each_dict:
        _format_img_path(inlet_infos, file_dir, each_key)


def _format_img_path(info, file_dir, img_key):
    if img_key in info:
        img_name = info.get(img_key, None)
        if img_name:
            info[img_key] = os.path.join(file_dir, img_name)


def deep_update_dict_values(origin, updateinfo, except_keys=[]):
    for key in updateinfo:
        if key not in origin:
            origin[key] = updateinfo[key]
            continue
        if key in except_keys:
            continue
        updatevalue = updateinfo[key]
        origin_value = origin[key]
        # if type(updatevalue) != type(origin_value):
        #     raise Exception('两个字典中信息类型不统一,key:{}'.format(key))

        if isinstance(updatevalue, dict):
            deep_update_dict_values(origin_value, updatevalue)
        else:
            origin[key] = updateinfo[key]


@gen.coroutine
def rollback_mch_payments(self_obj, change_id, change_type=1):
    result = yield select_change_record(self_obj, change_id, change_type)
    if result:
        change_records = result[1]
        if isinstance(change_records, dict):
            # 取出所有需要生效的数据
            if 'payment' in change_records:
                payments = change_records['payment']
                changed_payments = dict()
                if isinstance(payments, list):
                    for each_payment in payments:
                        changed_payments[each_payment[0]] = {'pay_type': each_payment[0],
                                                             'pay_rate': each_payment[1], 'pre_status': each_payment[2]}
                else:
                    changed_payments = payments

                for paytype in changed_payments:
                    record = changed_payments[paytype]
                    payment_type = record['pay_type']
                    payment_rate = record['pay_rate']
                    exist_status = record['pre_status']

                    table_name = 'dt_payment' if change_type == 1 else 'mch_payment'
                    id_name = 'dt_id' if change_type == 1 else 'mch_id'

                    # 更新支付费率的信息
                    sql = """update %s set activated_status=%s where %s=%s and payment_type=%s;"""
                    self_obj.db.executeSQL(sql, (table_name, exist_status, id_name, change_id, payment_type))
