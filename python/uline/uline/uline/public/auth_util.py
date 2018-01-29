#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: v0.0.1
# author: leiyutian
# contact: leiyutian@ulaiber.com
# filename: auth_util.py
# datetime: 2017/7/18 12:03
# description: 审核通过

import json
import traceback
import hashlib
import os

from uline.model.uline.info import (MchPayment, MchInletInfo, DtInletInfo, MchInletToWxInfo, MchBalance, D0WithdrawFee,
                                    RoleExtensionInfos)
from uline.model.uline.other import ChangeRecord, AuthMchInfo, DailyCutRecord
from uline.model.uline.user import MchUser, DtUser, BkUser
from uline.public import constants
from uline.public import log, common
from uline.settings import DINE_CHANNEL_ID
from uline.utils.alipay.get_code_by_name import query_code_by_name
from uline.utils.alipay.query_alipay import ali_api_block
from uline.utils.wxpay import query_wx
from uline.utils.wxpay.util import deal_with_wx_result
from uline.settings import FEATURE_SWITCH

CHANNELS = ['wx_offline', 'wx_online', 'ali', 'wx_dine', 'wx_dine_shop']
CHANNELS_ERROR_MSG = {
    'wx_offline': '微信支付进件:{}',
    'wx_online': '微信APP进件:{}',
    'ali': '支付宝进件:{}',
    'wx_dine': '微信围餐进件:{}',
    'wx_dine_shop': '微信围餐门店信息:{}'
}

AUTH_INIT = 0
AUTH_SUCCESS = 2
AUTH_FAIL = 1

WX_D0_PAYS = constants.ONLINE_D0_WX_PAY_TYPES + constants.OFFLINE_D0_WX_PAY_TYPES
WX_D1_PAYS = constants.D1_WX_PAY_TYPES
ALI_D0_PAYS = constants.D0_ALI_PAY_TYPES
ALI_D1_PAYS = constants.D1_ALI_PAY_TYPES


def print_auth_status(status):
    open_review = FEATURE_SWITCH['REVIEW']
    status_str = constants.AUTH_STATUS.get(str(status), u'审核不通过')
    if not open_review:
        if status in [constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD]:
            status_str = '审核中'
        elif status in [constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY]:
            status_str = '审核驳回'

    return status_str


def print_auth_status_simple(status):
    status_str = constants.AUTH_STATUS.get(str(status), '')
    if status in [constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD, constants.AUTH_STATUS_INLETING,
                  constants.AUTH_STATUS_INTERNET_FAIL]:
        status_str = '审核中'
    elif status in [constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY]:
        status_str = '审核驳回'
    return status_str


class MchAuthUtil(object):
    """
    商户审核操作相关工具类
    """

    def __init__(self, uline_session, bk_id, mch_id, **kwargs):
        self.uline_session = uline_session
        self.bk_id = bk_id
        self.mch_id = mch_id

        self.mch_wx_payment = False
        self.mch_wx_app_payment = False
        self.mch_ali_payment = False
        self.mch_wx_dine_payment = False
        self.wx_d0_payment = False
        self.ali_d0_payment = False
        self.current_time = common.timestamp_now()
        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER')
        self.db_change_record = None
        self.has_been_authed = False
        self.auth_result = ''
        self.auth_msg = ''
        self.mch_status = AUTH_INIT
        self.validate_status = kwargs.get('validate_status', False)
        # 进件到第三方结果
        self.inlet3party_success = True
        # 进件到第三方是否有网络问题
        self.has_internet_error = False
        self.inlet_result = {channel: {'result': True, 'result_msg': '', 'sub_mch_id': ''} for channel in CHANNELS}
        self.wx_dine_annex_img_keys = ['wx_dine_annex_img' + str(i) for i in range(1, 6)]
        self.has_daily_changes = False
        self.has_wx_d0_before = False
        self.has_wx_d0_after = False
        self.has_wx_d1_before = False
        self.has_wx_d1_after = False
        self.has_ali_d0_before = False
        self.has_ali_d0_after = False
        self.has_ali_d1_before = False
        self.has_ali_d1_after = False
        self.has_wx_dine_before = False
        self.daily_cut_record_payment = {}
        self.daily_cut_record_withdraw = {}

        self.init_result, self.init_msg = self.initialize()
        self.open_daily_cut = FEATURE_SWITCH.get('OPEN_DAILY_CUT', False) and self.has_been_authed

    def auth_mch(self):
        # 必须是进件中状态才能审核,一般配合start_auth()方法使用
        log.exception.info('start auth mch')
        if self.validate_status and self.mch_inlet_info.auth_status not in [constants.AUTH_STATUS_INLETING]:
            return common.scc_rsp(code=406, msg=u'审核时商户审核状态无效')
        auth_result = common.scc_rsp(code=200, msg='success')
        need_notify = False
        try:
            # 商户不能同时使用围餐通道和普通通道
            is_channel_conflict = (self.mch_wx_dine_payment and (
                self.mch_wx_payment or self.mch_wx_app_payment)) if self.init_result else False
            if self.init_result and not is_channel_conflict and self.mch_inlet_info.cs_id:
                # 更新连锁商户信息到门店
                result = self.update_chain_sub_mch_id(self.mch_inlet_info.cs_id)
                if not result:
                    self.inlet_result['wx_offline']['result_msg'] = u'复制连锁商户相关信息时出错'
                    self.inlet_result['wx_offline']['result'] = False
            elif self.init_result and not is_channel_conflict:
                self.inlet3party()
            elif self.init_result and is_channel_conflict:
                self.inlet_result['wx_offline']['result_msg'] = u'商户不能同时使用围餐通道和普通通道'
                self.inlet_result['wx_offline']['result'] = False
            # 检查进件到第三方结果
            self.check_inlet3party_result()
            # 如果初始化失败， 则提示失败就好
            if not self.init_result:
                auth_result = common.f_rsp(code=407, msg=self.init_msg)
            # 如果进件到第三方有网络错误，则覆盖原有的信息,审核状态改为进件失败
            elif self.has_internet_error:
                self.deal_auth_inlet(constants.AUTH_STATUS_INTERNET_FAIL, u'网络错误')
            # 如果进件到第三方信息中，有返回失败，则驳回
            elif not self.inlet3party_success:
                auth_result = common.f_rsp(code=406, msg=u"进件到支付宝或微信失败")
                # 状态修改为进件失败, 需要银行点击审核驳回, 然后通知商户
                self.mch_status = AUTH_FAIL
                self.deal_inlet3dparty_fail(self.inlet3party_msg)
            else:
                # 处理成功状态
                # todo-lei 进件围餐商户信息
                self.deal_auth_inlet(constants.AUTH_STATUS_ACCEPT,
                                     constants.AUTH_STATUS[str(constants.AUTH_STATUS_ACCEPT)])
                self.mch_status = AUTH_SUCCESS
                need_notify = True
        except Exception:
            log.exception.error(traceback.format_exc())
            self.uline_session.rollback()
            auth_result = common.f_rsp(code=406, msg='fail')
            need_notify = False
        else:
            try:
                self.uline_session.commit()
            except Exception:
                log.exception.error(traceback.format_exc())
                self.uline_session.rollback()
                auth_result = common.f_rsp(code=406, msg='fail')
                need_notify = False

        auth_result['mch_status'] = self.mch_status
        auth_result['need_notify'] = need_notify
        return auth_result

    def start_auth(self):
        """
        开始审核,将商户审核状态置为进件中
        """
        # 需要检验状态时,只能在初审中、复审中、进件失败三种状态下调用
        log.exception.info('start auth, mch_id:{}'.format(self.mch_id))
        if self.validate_status and self.mch_inlet_info.auth_status not in [constants.AUTH_STATUS_SUBMIT,
                                                                            constants.AUTH_STATUS_PREVIEWD,
                                                                            constants.AUTH_STATUS_INTERNET_FAIL]:
            return common.scc_rsp(code=406, msg=u'审核时商户审核状态无效')
        start_result = common.scc_rsp(code=200, msg='inleting')
        try:
            self.mch_inlet_info.auth_status = constants.AUTH_STATUS_INLETING
        except Exception:
            log.exception.info(traceback.format_exc())
            self.uline_session.rollback()
            start_result = common.f_rsp(code=406, msg='fail')
        else:
            try:
                self.uline_session.commit()
            except Exception:
                log.exception.info(traceback.format_exc())
                self.uline_session.rollback()
                start_result = common.f_rsp(code=406, msg='fail')
        return start_result

    def deal_auth_inlet(self, auth_status, comment):
        """
        进件结果处理
        Args:
            auth_status: 审核结果状态
            comment: 审核结果信息
        """
        # 保存第三方子商户号
        if self.inlet3party_success:
            wx_sub_mch_id = self.inlet_result['wx_offline'].get('sub_mch_id', '')
            if wx_sub_mch_id:
                self.mch_user.wx_sub_mch_id = wx_sub_mch_id

            wx_dine_sub_mch_id = self.inlet_result['wx_dine'].get('sub_mch_id', '')
            if wx_dine_sub_mch_id:
                self.mch_user.wx_sub_mch_id = wx_dine_sub_mch_id

            wx_app_sub_mch_id = self.inlet_result['wx_online'].get('sub_mch_id', '')
            if wx_app_sub_mch_id:
                self.mch_user.wx_app_sub_mch_id = wx_app_sub_mch_id

            ali_sub_mch_id = self.inlet_result['ali'].get('sub_mch_id', '')
            if ali_sub_mch_id:
                self.mch_user.ali_sub_mch_id = ali_sub_mch_id

        # 状态保存
        self.mch_user.status = auth_status
        self.mch_user.update_at = self.current_time
        self.mch_inlet_info.auth_status = auth_status
        self.mch_inlet_info.update_at = self.current_time
        self.add_auth_info(auth_status, comment)

        # 更新日志中的文件
        self.update_changes()
        self.update_activated_status()
        if self.db_change_record:
            change_record_status = constants.CHANGE_RECORD_STATUS_ACCEPT
            if self.has_daily_changes:
                change_record_status = constants.CHANGE_RECORD_STATUS_TO_CUT
            self.db_change_record.status = change_record_status
        log.exception.info('mch_auth update info success')

    def deal_inlet3dparty_fail(self, show_comment):
        # 进件失败处理
        auth_status = constants.AUTH_STATUS_INTERNET_FAIL
        if hasattr(self, 'bk_user'):
            self.add_auth_info(auth_status, show_comment)
        # if hasattr(self, 'change_record'):
        #     self.rollback_payments()
        if hasattr(self, 'mch_inlet_info'):
            self.status = auth_status
            self.mch_inlet_info.auth_status = auth_status
            self.mch_inlet_info.update_at = self.current_time

    def add_auth_info(self, auth_status, comment):
        """
        添加审核信息
        Args:
            auth_status: 审核状态
            comment: 审核信息
        """
        auth_info = AuthMchInfo()
        auth_info.mch_id = self.mch_id
        auth_info.comment = comment
        auth_info.auth_user = self.bk_user.email
        auth_info.auth_status = auth_status
        auth_info.create_at = self.current_time
        self.uline_session.add(auth_info)

    def initialize(self):
        """
        初始化信息
        """
        db_payments = self.uline_session.query(MchPayment).filter(MchPayment.mch_id == self.mch_id).all()
        db_paytypes = {}
        self.db_payments = {}
        for each_payment in db_payments:
            payment_type = each_payment.payment_type
            db_paytypes[payment_type] = payment_type
            self.db_payments[payment_type] = each_payment
            if payment_type in WX_D0_PAYS:
                self.has_wx_d0_before = True
            if payment_type in WX_D1_PAYS:
                self.has_wx_d1_before = True
            if payment_type in ALI_D0_PAYS:
                self.has_ali_d0_before = True
            if payment_type in ALI_D1_PAYS:
                self.has_ali_d1_before = True
            if payment_type in constants.DINNER_TOGGETHER_PAY_TYPES:
                self.has_wx_dine_before = True

        self.mch_user = self.uline_session.query(MchUser).filter(MchUser.mch_id == self.mch_id).first()
        self.mch_inlet_info = self.uline_session.query(MchInletInfo).filter(MchInletInfo.mch_id == self.mch_id).first()
        if not self.mch_inlet_info:
            return False, u'无对应商户进件信息'
        log.exception.info('current mch auth status:{}'.format(self.mch_inlet_info.auth_status))
        # 更新的信息
        self.change_record = self.get_update_changes()
        inlet3dparty_keys = ['mch_name', 'mch_shortname', 'service_phone', 'contact', 'mobile', 'email', 'address',
                             'city', 'district', 'wx_ind_code', 'ali_ind_code']
        self.inlet3dparty_info = {}
        for key_name in inlet3dparty_keys:
            self.inlet3dparty_info[key_name] = self.change_record.get(key_name, getattr(self.mch_inlet_info, key_name))

        self.wx_business_no = self.inlet3dparty_info['wx_ind_code'] or self.mch_inlet_info.old_ind_code
        changed_payments = self.change_record.get('payment', {})
        for payment_type in changed_payments:
            payment = changed_payments[payment_type]
            payment_type = int(payment.get('pay_type', 0))
            action_type = payment.get('action_type', 2)
            if action_type in (1, 2):
                db_paytypes[payment_type] = payment_type
            elif action_type == 3 and payment_type in db_paytypes:
                del db_paytypes[payment_type]
        for payment_type in db_paytypes:
            if payment_type in constants.WX_OFFLINE_PAYTYPES:
                self.mch_wx_payment = True
            if payment_type in constants.WX_ONLINE_PAYTYPES:
                self.mch_wx_app_payment = True
            if payment_type in constants.ALI_PAYTYPES:
                self.mch_ali_payment = True
            if payment_type in constants.DINNER_TOGGETHER_PAY_TYPES:
                self.mch_wx_dine_payment = True
            if payment_type in WX_D0_PAYS:
                self.has_wx_d0_after = True
            if payment_type in WX_D1_PAYS:
                self.has_wx_d1_after = True
            if payment_type in ALI_D0_PAYS:
                self.has_ali_d0_after = True
            if payment_type in ALI_D1_PAYS:
                self.has_ali_d1_after = True
        self.dt_info = self.uline_session.query(DtInletInfo).filter(
            DtInletInfo.dt_id == self.mch_inlet_info.dt_id).first()
        self.dt_user = self.uline_session.query(DtUser).filter(DtInletInfo.dt_id == self.mch_inlet_info.dt_id).first()
        if not self.dt_info:
            return False, u'商户无对应的渠道商信息'
        self.bk_user = self.uline_session.query(BkUser).filter(BkUser.bk_id == self.bk_id).first()
        if not self.bk_user:
            return False, u'无当前银行用户信息'
        self.withdraw_fee = self.uline_session.query(D0WithdrawFee).filter(D0WithdrawFee.role == self.mch_id,
                                                                           D0WithdrawFee.role_type == 'mch').first()
        self.has_been_authed = self.is_authed()
        return True, ''

    def get_update_changes(self):
        change_record = self.uline_session.query(ChangeRecord).filter(ChangeRecord.mch_id == self.mch_id,
                                                                      ChangeRecord.status == 1).first()
        if change_record:
            self.db_change_record = change_record
            change_data = json.loads(change_record.data_json)
            if isinstance(change_data, dict):
                return change_data
        return {}

    def update_chain_sub_mch_id(self, cs_id):
        """连锁门店时复制连锁商户信息"""
        result = False
        chain_user = self.uline_session.query(DtUser).filter(DtUser.dt_id == cs_id).first()
        if chain_user:
            self.mch_user.wx_sub_mch_id = chain_user.wx_sub_mch_id
            self.mch_user.wx_app_sub_mch_id = chain_user.wx_app_sub_mch_id
            self.mch_user.ali_sub_mch_id = chain_user.ali_sub_mch_id
            result = True
        return result

    def mch_inlet_to_wx(self, wx_sub_id, channel_id, channel):
        """商户进件到微信"""
        # 微信支付(扫码支付／刷卡支付／公众账号支付)
        result = True
        msg_wx = "success"
        sub_mch_id = ''
        # 如果是0费率, 进件到0费率的服务商下面
        if not wx_sub_id:
            inlet_data = {
                # ['mch_name', 'mch_shortname', 'service_phone', 'contact', 'mobile', 'email', 'address',
                #  'city', 'district']
                'merchant_name': self.inlet3dparty_info['mch_name'],
                'merchant_shortname': self.inlet3dparty_info['mch_shortname'],
                'service_phone': self.inlet3dparty_info['service_phone'] or self.inlet3dparty_info['mobile'],
                'contact': self.inlet3dparty_info['contact'],
                'contact_phone': self.inlet3dparty_info['mobile'],
                'contact_email': self.inlet3dparty_info['email'],
                'business': self.wx_business_no,
                'merchant_remark': self.mch_id,
                'channel_id': channel_id,
            }
            ret = query_wx.query_wx_api_block(inlet_data, query_type='create_mch', channel=channel)
            log.exception.info('inlet_wx_create, channel:{}, result:{}'.format(channel, ret))
            self.save_mch_inlet_to_wx(ret)

            default_err_msg = '进件到微信支付出现未知错误,请联系客服!'
            sub_mch_id, msg_wx = deal_with_wx_result(ret, 'sub_mch_id', default_err_msg)
            if not sub_mch_id:
                result = False
        elif wx_sub_id:
            # 修改微信端商户信息(包括商户简称和服务电话)
            sub_mch_id = wx_sub_id
            update_infos = {
                'merchant_shortname': self.inlet3dparty_info['mch_shortname'],
                'service_phone': self.inlet3dparty_info['service_phone'] or self.inlet3dparty_info['mobile'],
                'sub_mch_id': wx_sub_id
            }
            update_result = query_wx.query_wx_api_block(update_infos, query_type='modify_mch', channel=channel)
            log.exception.info('inlet_wx_update, channel:{}, result:{}'.format(channel, update_result))
            self.save_mch_inlet_to_wx(update_result)
            default_err_msg = '更新微信支付出现未知错误,请联系客服!'
            deal_result, msg_wx = deal_with_wx_result(update_result, 'result_code', default_err_msg)
            if deal_result != 'SUCCESS':
                result = False
        result_info = {
            'result': result,
            'result_msg': msg_wx,
            'sub_mch_id': sub_mch_id
        }
        return result_info

    def save_mch_inlet_to_wx(self, inlet_result):
        mch_inlet_wx_info = MchInletToWxInfo()
        mch_inlet_wx_info.mch_id = self.mch_id
        mch_inlet_wx_info.return_code = inlet_result.get('code', 'FAIL')
        mch_inlet_wx_info.return_msg = inlet_result.get('msg', 'FAIL')
        mch_inlet_wx_info.result_code = inlet_result.get('sub_code', 'FAIL')
        mch_inlet_wx_info.result_msg = inlet_result.get('sub_msg', 'FAIL')
        mch_inlet_wx_info.create_at = self.current_time
        self.uline_session.add(mch_inlet_wx_info)

    def rollback_payments(self):
        result = self.change_record.get("payment", {})
        payments = dict()
        if result:
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
                    self.uline_session.query(MchPayment).filter(MchPayment.mch_id == self.mch_id,
                                                                MchPayment.payment_type == payment_type).update(
                        {'activated_status': payment['pre_status']})
        if self.db_change_record:
            self.db_change_record.status = 3

    def mch_inlet_to_ali_reg(self, ali_mch_id):
        ali_flag = True
        msg_ali = ""
        ret = self.create_alipay_sub_mch_id(update=bool(ali_mch_id))
        self.save_mch_inlet_to_wx(ret)
        ali_sub_mch_id = ret.get('sub_merchant_id') if ret.get('code') in ['10000', 10000] else ''
        if not ali_sub_mch_id:
            ali_flag = False
            msg_ali = ret.get('sub_msg', '进件到支付宝发生未知错误,请联系客服!')

        result_info = {
            'result': ali_flag,
            'result_msg': msg_ali,
            'sub_mch_id': ali_sub_mch_id
        }
        return result_info

    def create_alipay_sub_mch_id(self, update=False):
        # 鉴于目前更新和新增一样，不做不同处理，保留upate字段，防止后期支付宝修改
        query_dict = {'external_id': self.mch_id, 'name': self.inlet3dparty_info['mch_name'],
                      'alias_name': self.inlet3dparty_info['mch_shortname'],
                      'service_phone': self.inlet3dparty_info['service_phone'] or self.inlet3dparty_info['mobile'],
                      'category_id': self.inlet3dparty_info['ali_ind_code']}

        level = 'M1'
        # 如果有填区域信息，则以M2等级进件
        if self.mch_inlet_info.district:
            province_code, city_code, district_code = query_code_by_name(self.mch_inlet_info.province,
                                                                         self.mch_inlet_info.city,
                                                                         self.mch_inlet_info.district)
            if province_code and city_code and district_code:
                query_dict['address_info'] = [{
                    'province_code': province_code,
                    'city_code': city_code,
                    'district_code': district_code,
                    'address': self.inlet3dparty_info['address'],
                    'type': 'BUSINESS_ADDRESS'
                }]
                level = 'M2'
        ali_ret = ali_api_block(query_dict, 'indirect_modify' if update else 'indirect_create', require_param_key=level)
        return ali_ret

    def update_changes(self):
        # 将商户修改信息覆盖到对应表中
        if self.change_record and isinstance(self.change_record, dict):
            new_mobile = self.change_record.get('mobile', None)
            if new_mobile:
                old_mobile = self.mch_inlet_info.mobile
                result = common.bcrypt_pwd_block(str(old_mobile), self.mch_user.password)
                # 如果reesult为True,说明该渠道商还未登录，mobile已经被修改了
                if result:
                    # 将密码修改为新的联系电话
                    new_password = common.bcrypt_pwd_new(str(new_mobile))
                    self.mch_user.password = new_password

            change_email = self.change_record.get('email', None)
            if change_email:
                self.mch_user.email = change_email

            if 'payment' in self.change_record:
                payments = self.change_record['payment']
                self.update_mch_payments(payments)

            if 'del_annex' in self.change_record:
                del_annex = self.change_record['del_annex']
                self.delete_mch_annex_img(del_annex)

            if 'del_wx_dine_annex' in self.change_record:
                self.delete_mch_dine_annex_img(self.change_record.get('del_wx_dine_annex', ''))

            if 'balance_info' in self.change_record:
                balance_update_info = self.change_record['balance_info']
                update_keys = ['balance_type', 'balance_name', 'bank_no', 'balance_account', 'id_card_no']
                change_balance_info = {key: balance_update_info[key] for key in update_keys if
                                       key in balance_update_info}
                db_balance_info = self.uline_session.query(MchBalance).filter(MchBalance.mch_id == self.mch_id).first()
                if db_balance_info:
                    for each_key in change_balance_info:
                        setattr(db_balance_info, each_key, change_balance_info[each_key])

            if 'role' in self.change_record:
                update_withdrawinfo = self.change_record.get('role', {})
                if update_withdrawinfo:
                    self.update_withdraw_info(update_withdrawinfo)

            self.update_inlet_infos()
            self.update_extensions()
            if self.change_record:
                cut_info = {}
                if self.daily_cut_record_withdraw:
                    cut_info['withdraw'] = self.daily_cut_record_withdraw
                if self.daily_cut_record_payment:
                    cut_info['payment'] = self.daily_cut_record_payment
                if cut_info:
                    cut_info['change_record_id'] = self.db_change_record.id
                    daily_cut_record = DailyCutRecord()
                    daily_cut_record.record_json = json.dumps(cut_info)
                    daily_cut_record.role_id = self.mch_id
                    daily_cut_record.role_type = 'mch'
                    daily_cut_record.status = 1
                    self.uline_session.add(daily_cut_record)

        db_payments = self.uline_session.query(MchPayment).filter(MchPayment.mch_id == self.mch_id).all()
        has_wx_dine = False
        has_wx_d0 = False
        wx_d0_pays = constants.ONLINE_D0_WX_PAY_TYPES + constants.OFFLINE_D0_WX_PAY_TYPES
        for each_payment in db_payments:
            payment_type = each_payment.payment_type
            if not has_wx_d0 and payment_type in wx_d0_pays:
                has_wx_d0 = True
            if not has_wx_dine and payment_type in constants.DINNER_TOGGETHER_PAY_TYPES:
                has_wx_dine = True
        withdraw_fee = self.uline_session.query(D0WithdrawFee).filter(D0WithdrawFee.role == self.mch_id,
                                                                      D0WithdrawFee.role_type == 'mch').first()
        if not has_wx_d0 and withdraw_fee:
            # 如果有围餐且有微信提现手续费
            withdraw_fee.wx = None
        if not has_wx_dine:
            # 如果没有围餐支付方式，则需要删除所有的围餐信息，暂时全删掉
            self.uline_session.query(RoleExtensionInfos).filter(RoleExtensionInfos.role_id == self.mch_id,
                                                                RoleExtensionInfos.role_type == 'mch').delete()

    def update_mch_payments(self, payments):
        changed_payments = dict()
        has_wx_d_change = ((self.has_wx_d0_before or self.has_wx_dine_before) and self.has_wx_d1_after) or (
            (self.has_wx_d1_before or self.has_wx_dine_before) and self.has_wx_d0_after)
        has_ali_d_change = (self.has_ali_d0_before and self.has_ali_d1_after) or (
            self.has_ali_d1_before and self.has_ali_d0_after)
        # 是否有
        has_dine_change = (self.has_wx_d1_before or self.has_wx_d0_before) and self.mch_wx_dine_payment
        log.uline_celery.info(
            'has_wx_d_change:{}, has_ali_d_change:{}, has_dine_change:{}'.format(has_wx_d_change, has_ali_d_change,
                                                                                 has_dine_change))
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
            action_type = record.get('action_type', 2)

            in_wx_d_change = action_type in constants.WX_PAY_TYPES and has_wx_d_change
            in_ali_d_change = action_type in constants.ALI_PAYTYPES and has_ali_d_change
            in_wx_dine_change = action_type in constants.DINNER_TOGGETHER_PAY_TYPES and has_dine_change
            in_channel_or_cycle_change = in_wx_d_change or in_ali_d_change or in_wx_dine_change
            db_payment = self.db_payments.get(int(payment_type), None)

            # action_type 动作，1：新增，2：更新，3: 删除
            if action_type == 2 and db_payment:
                activated_status = 1
                # 查询支付方式的原有费率，如果有且等于更新的费率，则需要还原为原有的激活状态
                # 如果在数据库中已经存在
                if db_payment:
                    exist_rate = db_payment.payment_rate
                    # 如果费率前后相等，则不用修改费率，状态还原为原有的状态（为兼容已有的数据）
                    if exist_rate and exist_rate == payment_rate:
                        activated_status = exist_status
                    # 更新支付费率的信息
                    if not self.open_daily_cut:
                        db_payment.payment_rate = payment_rate
                        db_payment.activated_status = activated_status
                    else:
                        self.has_daily_changes = True
                        self.daily_cut_record_payment[int(payment_type)] = {
                            'pre_payment_rate': db_payment.payment_rate,
                            'pre_payment_status': db_payment.activated_status,
                            'update_payment_rate': payment_rate,
                            'payment_type': payment_type,
                            'action_type': action_type
                        }
            elif action_type == 1 and not db_payment:
                if self.open_daily_cut and in_channel_or_cycle_change:
                    self.daily_cut_record_payment[int(payment_type)] = {
                        'pre_payment_rate': payment_rate,
                        'pre_payment_status': 2,
                        'update_payment_rate': payment_rate,
                        'payment_type': payment_type,
                        'action_type': action_type
                    }
                else:
                    payment = MchPayment()
                    payment.mch_id = self.mch_id
                    payment.payment_type = payment_type
                    payment.payment_rate = payment_rate
                    payment.activated_status = 1
                    payment.create_at = self.current_time
                    payment.update_at = self.current_time
                    self.uline_session.add(payment)
            elif action_type == 3 and db_payment:
                if self.open_daily_cut and in_channel_or_cycle_change:
                    self.daily_cut_record_payment[int(payment_type)] = {
                        'pre_payment_rate': db_payment.payment_rate,
                        'pre_payment_status': db_payment.activated_status,
                        'update_payment_rate': payment_rate,
                        'payment_type': payment_type,
                        'action_type': action_type
                    }
                else:
                    self.uline_session.delete(db_payment)
        self.uline_session.flush()

    def update_withdraw_info(self, update_withdrawinfo):
        wx_withdraw = update_withdrawinfo.get('wx', None)
        alipay_withdraw = update_withdrawinfo.get('alipay', None)
        # 需要立即更新的数据
        db_upate_infos = {}

        # 如果更新前后都没有d0支付方式，则即时生效,因为提现手续费对d1无效
        if self.has_wx_d0_before and self.has_wx_d0_after and self.open_daily_cut:
            self.daily_cut_record_withdraw['wx'] = wx_withdraw
        else:
            db_upate_infos['wx'] = wx_withdraw

        if self.has_ali_d0_before and self.has_ali_d0_before and self.open_daily_cut:
            self.daily_cut_record_withdraw['alipay'] = alipay_withdraw
        else:
            db_upate_infos['alipay'] = alipay_withdraw

        if db_upate_infos:
            if not self.withdraw_fee:
                update_info = {
                    'update_at': self.current_time,
                    'role': self.mch_id,
                    'role_type': 'mch',
                    'create_at': self.current_time
                }
                update_info.update(db_upate_infos)
                self.uline_session.add(D0WithdrawFee(**update_info))
            else:
                for each_key in db_upate_infos:
                    setattr(self.withdraw_fee, 'wx', db_upate_infos[each_key])
                self.withdraw_fee.update_at = self.current_time

    def is_withdraw_change(self):
        """是否有D0手续费更新"""
        has_withdraw_change = False
        if 'role' in self.change_record:
            update_withdrawinfo = self.change_record.get('role', {})
            if update_withdrawinfo:
                wx_withdraw = update_withdrawinfo.get('wx', None)
                alipay_withdraw = update_withdrawinfo.get('alipay', None)
                has_withdraw_change = not (self.withdraw_fee and self.withdraw_fee.wx == wx_withdraw and
                                           self.withdraw_fee.alipay == alipay_withdraw)
        return has_withdraw_change

    def auth_password(self, password):
        return common.bcrypt_pwd_block(password, self.mch_user.password)

    def update_inlet_infos(self):
        need_update_keys = ["province", "city", "license_period", "mobile", "mch_shortname", "license_scope",
                            "mch_name", "service_phone", "contact", "license_num", "email", "address",
                            'id_card_img_f', 'id_card_img_b', 'license_img', 'license_start_date', 'notify_url'
                                                                                                   'license_end_date',
                            'dt_sub_id', 'u_ind_code', 'wx_ind_code', 'ali_ind_code',
                            'cs_id']
        need_update_keys += ['annex_img' + str(i) for i in range(1, 6)]
        change_inlet_info = {key: self.change_record[key] for key in need_update_keys if
                             key in self.change_record}
        if change_inlet_info:
            for each_key in change_inlet_info:
                setattr(self.mch_inlet_info, each_key, change_inlet_info.get(each_key, None))

    def update_extensions(self):
        update_extension_infos = ['mch_inner_img', 'mch_front_img', 'mch_desk_img']
        update_extension_infos.extend(self.wx_dine_annex_img_keys)
        change_extensions = {key: self.change_record[key] for key in update_extension_infos if
                             key in self.change_record}
        extensions_map = dict()
        extensions_db = self.uline_session.query(RoleExtensionInfos).filter(RoleExtensionInfos.role_id == self.mch_id,
                                                                            RoleExtensionInfos.role_type == 'mch').all()
        for each_extention in extensions_db:
            extensions_map[each_extention.extension_name] = each_extention
        for each_extention_name in change_extensions:
            change_value = change_extensions[each_extention_name]
            if each_extention_name in extensions_map:
                if change_value and (change_value != extensions_map[each_extention_name]):
                    extension_in_db = extensions_map[each_extention_name]
                    extension_in_db.extension_value = change_value
                    extension_in_db.update_time = self.current_time
            else:
                infos = {
                    'role_id': self.mch_id,
                    'role_type': 'mch',
                    'extension_name': each_extention_name,
                    'extension_value': change_value,
                    'create_time': self.current_time,
                    'update_time': self.current_time,
                }
                self.uline_session.add(RoleExtensionInfos(**infos))

    def update_activated_status(self):
        inlet_activated_status = 1
        db_activated_payments = self.uline_session.query(MchPayment).filter(MchPayment.mch_id == self.mch_id,
                                                                            MchPayment.activated_status == 2).all()
        if db_activated_payments:
            inlet_activated_status = 2
        self.mch_inlet_info.activated_status = inlet_activated_status

    def inlet3party(self):
        try:
            if self.mch_wx_payment:
                channel = 0 if self.dt_user.rate == 1 else 2
                log.exception.info('channel:{}'.format(channel))
                wx_inlet_result = self.mch_inlet_to_wx(self.mch_user.wx_sub_mch_id, self.dt_info.wx_channel_id, channel)
                self.inlet_result['wx_offline'].update(wx_inlet_result)

            if self.mch_wx_app_payment:
                wx_app_inlet_result = self.mch_inlet_to_wx(self.mch_user.wx_app_sub_mch_id,
                                                           self.dt_info.wx_app_channel_id,
                                                           6)
                self.inlet_result['wx_online'].update(wx_app_inlet_result)

            if self.mch_ali_payment:
                ali_inlet_result = self.mch_inlet_to_ali_reg(self.mch_user.ali_sub_mch_id)
                self.inlet_result['ali'].update(ali_inlet_result)

            if self.mch_wx_dine_payment and self.open_dine:
                wx_dine_inlet_result = self.mch_inlet_to_wx(self.mch_user.wx_sub_mch_id, DINE_CHANNEL_ID, 10)
                self.inlet_result['wx_dine'].update(wx_dine_inlet_result)
                # self.inlet_result['wx_dine_shop'] = self.inlet_wx_dine()
            log.uline_celery.info(self.inlet_result)

        except Exception:
            log.exception.error(traceback.format_exc())
            self.has_internet_error = True

    def check_inlet3party_result(self):
        error_msgs = list()
        for each_channel in CHANNELS:
            each_inlet_result = self.inlet_result[each_channel]
            if not each_inlet_result['result']:
                self.inlet3party_success = False
                error_msgs.append(CHANNELS_ERROR_MSG[each_channel].format(each_inlet_result['result_msg']))
        self.inlet3party_msg = " ".join(error_msgs)

    def inlet_wx_dine(self):
        """围餐门店进件"""
        shop_id = ''
        if shop_id:
            wx_status, reject_msg = self.query_wx_dine_result(shop_id)
        if not self.mch_inlet_info.district:
            return {'result': False, 'result_msg': u'商户没有地址区域信息', 'sub_mch_id': shop_id}
        _, _, district_code = query_code_by_name(self.mch_inlet_info.province,
                                                 self.mch_inlet_info.city,
                                                 self.mch_inlet_info.district)
        extensions_db = self.uline_session.query(RoleExtensionInfos).filter(RoleExtensionInfos.role_id == self.mch_id,
                                                                            RoleExtensionInfos.role_type == 'mch').all()
        media_map = dict()
        base_dir = '/static/uploads/mch/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
        dine_img_keys = {
            'mch_inner_img': 'indoor_pic',
            'mch_front_img': 'shop_entrance_pic',
            'mch_desk_img': 'checkstand_pic'
        }
        dine_annex_img_keys = self.wx_dine_annex_img_keys
        img_path_map = dict()
        dine_annex_imgs = dict()
        for each_extension in extensions_db:
            media_name = each_extension.extension_name
            media_value = each_extension.extension_value
            if media_name in dine_img_keys:
                media_path = os.path.join(file_dir, media_value) if media_value else None
                if not media_path:
                    return {'result': False, 'result_msg': u'商户围餐门店图片信息不全', 'sub_mch_id': shop_id}
                img_path_map[dine_img_keys[media_name]] = media_path
            elif media_name == 'shop_id':
                shop_id = media_value
            elif media_name in dine_annex_img_keys:
                media_path = os.path.join(file_dir, media_value) if media_value else None
                if media_path:
                    dine_annex_imgs[media_name] = media_path
        del_wx_dine_indexs = self.change_record.get('del_wx_dine_annex', '')
        # 删除的部分信息
        if del_wx_dine_indexs:
            for each_index in del_wx_dine_indexs:
                img_key = 'wx_dine_annex_img' + str(each_index)
                del dine_annex_imgs[img_key]
        for img_key in self.wx_dine_annex_img_keys:
            if img_key in self.change_record:
                media_value = self.change_record[img_key] or None
                media_path = os.path.join(file_dir, media_value) if media_value else None
                if media_path:
                    dine_annex_imgs[img_key] = media_path
        # 如果没有围餐的补充材料
        if not dine_annex_imgs:
            return {'result': False, 'result_msg': u'围餐商户没有补充材料', 'sub_mch_id': shop_id}

        license_img = self.mch_inlet_info.license_img
        license_path = os.path.join(file_dir, license_img) if license_img else None
        if not license_path:
            return {'result': False, 'result_msg': u'商户营业执照图片信息不全', 'sub_mch_id': shop_id}
        img_path_map['business_license_pic'] = license_path
        for each_name in img_path_map:
            media_id, msg_wx = self.inlet_wx_dine_img(img_path_map[each_name])
            if not media_id:
                return {'result': False, 'result_msg': msg_wx, 'sub_mch_id': shop_id}
            media_map[each_name] = media_id
        query_args = {
            'sub_mch_id': self.mch_user.wx_sub_mch_id,
            'shop_name': self.mch_inlet_info.mch_shortname,
            'shop_address_code': district_code,
            'shop_street': self.mch_inlet_info.address,
            'nonce_str': common.gen_random_str()
        }
        query_args.update(media_map)
        query_type = ''
        default_msg = ''
        if shop_id:
            wx_status, reject_msg = self.query_wx_dine_result(shop_id)
            if wx_status == constants.AUTH_STATUS_INTERNET_FAIL:
                query_args['shop_id'] = shop_id
                query_type = 'modifycsprofil'
                default_msg = u'修改围餐门店信息失败'
        elif not shop_id:
            query_type = 'greenplangetnewcs'
            default_msg = u'新增围餐门店信息失败'
        if query_type:
            result = query_wx.query_wx_api_block(query_args, query_type, channel=10)
            shop_id, result_msg = deal_with_wx_result(result, 'shop_id', default_error_msg=default_msg)
            if not shop_id:
                return {'result': False, 'result_msg': result_msg, 'sub_mch_id': shop_id}
        return {'result': True, 'result_msg': '', 'sub_mch_id': shop_id}

    def inlet_wx_dine_img(self, imgfile):
        """围餐图片进件"""
        md5info = hashlib.md5()
        with open(imgfile, 'rb') as f:
            file_content = f.read()
            md5info.update(file_content)
            file_md5 = md5info.hexdigest()

            file_headers = dict()
            file_headers['filename'] = f.name
            file_headers['filelength'] = len(file_content)
            files = [
                ('media', (os.path.basename(imgfile), file_content, query_wx.get_content_type(imgfile), file_headers))]

            args = {
                "media_hash": file_md5,
            }
            channel = 10
            ret = query_wx.query_wx_use_form(args, 'uploadpicturesapi', ['mch_id'], files, channel=channel)
            log.exception.info('inlet dine image, channel:{}, result:{}'.format(channel, ret))
            self.save_mch_inlet_to_wx(ret)

            default_err_msg = '更新图片到微信支付出现未知错误,请联系客服!'
            media_id, msg_wx = deal_with_wx_result(ret, 'media_id', default_err_msg)
            return media_id, msg_wx

    def query_deal_wx_dine_result(self):
        """查询并处理围餐结果"""
        wx_status, reject_msg = self.query_deal_wx_dine_result()
        auth_status = self.mch_inlet_info.auth_status
        pre_status = auth_status
        deal_result = common.scc_rsp(code=200, msg='success')
        try:
            if wx_status == constants.AUTH_STATUS_DENY:
                self.mch_inlet_info.auth_status = constants.AUTH_STATUS_INTERNET_FAIL
                auth_status = constants.AUTH_STATUS_INTERNET_FAIL
            elif wx_status == constants.AUTH_STATUS_ACCEPT:
                self.mch_inlet_info.auth_status = constants.AUTH_STATUS_ACCEPT
                auth_status = constants.AUTH_STATUS_ACCEPT
        except Exception:
            log.exception.info(traceback.format_exc())
            self.uline_session.rollback()
            deal_result = common.f_rsp(code=406, msg='fail')
            auth_status = pre_status
        else:
            try:
                self.uline_session.commit()
            except Exception:
                log.exception.info(traceback.format_exc())
                self.uline_session.rollback()
                deal_result = common.f_rsp(code=406, msg='fail')
                auth_status = pre_status
        return deal_result

    def query_wx_dine_result(self, shop_id):
        """查询围餐结果"""
        query_args = {
            'sub_mch_id': self.mch_user.wx_sub_mch_id,
            'shop_id': shop_id,
            'nonce_str': common.gen_random_str()
        }
        result = query_wx.query_wx_api_block(query_args, 'queryauthresult', channel=10)
        default_err_str = u'获取商户微信审核结果失败'
        apply_status, wx_msg = deal_with_wx_result(result, 'apply_status', default_err_str)
        if apply_status is None:
            return apply_status, wx_msg
        reject_reason = ''
        auth_status = self.mch_inlet_info.auth_status
        if apply_status == 'reject':
            # 微信侧驳回
            reject_reason = result.get('reject_reason', '')
            auth_status = constants.AUTH_STATUS_DENY
        elif apply_status == 'accept':
            # 微信侧通过
            auth_status = constants.AUTH_STATUS_ACCEPT
        elif apply_status == 'abnormal':
            # 微信侧在编辑(如果只使用接口不会出现此状态。如果出现此状态再调用一次修改就会变成待审核）
            pass
        elif apply_status == 'submit':
            # 微信侧待审核
            pass
        return auth_status, reject_reason

    def delete_mch_annex_img(self, del_annex):
        if del_annex and isinstance(del_annex, unicode):
            for del_img in del_annex.split("-"):
                setattr(self.mch_inlet_info, 'annex_img{}'.format(del_img), None)

    def delete_mch_dine_annex_img(self, del_annex_imgs):
        if del_annex_imgs:
            for each_index in del_annex_imgs:
                img_key = 'wx_dine_annex_img' + str(each_index)
                self.uline_session.query(RoleExtensionInfos).filter(RoleExtensionInfos.role_id == self.mch_id,
                                                                    RoleExtensionInfos.role_type == 'mch',
                                                                    RoleExtensionInfos.extension_name == img_key).delete()

    def is_authed(self):
        authed_count = self.uline_session.query(AuthMchInfo).filter(AuthMchInfo.mch_id == self.mch_id).filter(
            AuthMchInfo.auth_status == 2).count()
        return authed_count > 0
