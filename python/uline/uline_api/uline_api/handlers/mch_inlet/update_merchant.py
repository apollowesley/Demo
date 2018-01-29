#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '3/15/17'

import datetime
import json
import uuid
from datetime import date

import os
import tornado.escape
import tornado.gen
import tornado.web

from uline_api.handlers.baseHandlers import RESTfulHandler, RESTfulHTTPError
from uline_api.model.uline.info import (
    MchInletInfo, MchBalance, MchPayment, UlineIndustryInfo, IndustryAliInfo, D0WithdrawPay, DtPayment,
    RoleExtensionInfos,
    IndustryJDInfo)
from uline_api.model.uline.other import AuthMchInfo, ChangeRecord
from uline_api.model.uline.user import MchUser, DtUser
from uline_api.public.constants import old_payment_relations, NEW_AVAILABLE_PAYMENTS
from uline_api.public.constants import new_payment_relations
from uline_api.setting import env, PAY_TYPES, FEATURE_SWITCH, DINE_PAY_TYPES
from uline_api.settings import MIN_ALI_LEVEL
from uline_api.util.db import uline_session_scope
from uline_api.util.log import error_log
from .modify_form import UpdateMerchantlnletForm
from uline_api.public import constants
from uline.backend.risk import query_mch_risk_info


class UpdateMerchant(RESTfulHandler, UpdateMerchantlnletForm):
    def prepare(self):
        self.has_authed = True
        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER', False)
        use_dine = self.request.arguments.get('use_dine', [''])[0]
        self.jd_pay = FEATURE_SWITCH.get('JD_PAY')
        if self.open_dine and use_dine:
            for each_paytype in DINE_PAY_TYPES:
                self.request.arguments['payment_type' + str(each_paytype)] = ['0']
        if self.request.method == 'POST':
            self.update_at = datetime.datetime.now()
            super(UpdateMerchant, self).prepare()
            mch_id = self.get_argument('mch_id', None)
            if not mch_id:
                raise RESTfulHTTPError(400, content={'mch_id': [u'指定商户未找到']})
            self.mch_id = mch_id
            content = None
            with uline_session_scope() as session:
                mch_inlet_info = session.query(MchInletInfo).filter_by(mch_id=self.mch_id).first()
                if not mch_inlet_info:
                    content = {'mch_id': [u'指定商户未找到']}
                elif mch_inlet_info.auth_status in [constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_REVIEWING,
                                                    constants.AUTH_STATUS_INLETING,
                                                    constants.AUTH_STATUS_INTERNET_FAIL]:
                    content = {'mch_status': [u'商户正在审核中，无法修改']}
                else:
                    self.db_cs_id = mch_inlet_info.cs_id

                    # 如果是连锁门店，则删掉所有支付方式表单
                    if self.db_cs_id:
                        for payment_type in PAY_TYPES:
                            field_name = u'payment_type' + str(payment_type)
                            if field_name in self.request.arguments:
                                del self.request.arguments[u'payment_type' + str(payment_type)]

            if content:
                raise RESTfulHTTPError(400, content=content)

            self.form = UpdateMerchantlnletForm(self)
            setattr(self.form, 'dt_id', self.dt_id)
            # self.auth_status = 1
            self.change_dict = {}
            self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')

            # 本来是连锁门店且获取的连锁商户号为空，则取数据库中cs_id
            if self.db_cs_id and not self.cs_id:
                self.cs_id = self.db_cs_id
            elif not self.db_cs_id and self.cs_id:
                raise RESTfulHandler(400, content={'cs_id': [u'普通商户无法修改为连锁门店']})

    @tornado.gen.coroutine
    def post(self):
        mch_id = self.get_argument('mch_id', None)
        if not mch_id:
            raise RESTfulHTTPError(400, content={'mch_id': [u'指定商户未找到']})
        self.mch_id = mch_id
        content = None
        # 商户是否激活过
        has_authed = None

        has_wx_general = False
        has_wx_dine = False
        old_head_name = ''
        old_head_mobile = ''
        old_img_with_id_card = ''
        with uline_session_scope() as session:
            user = session.query(MchUser).filter_by(mch_id=self.mch_id).first()
            if not user:
                content = {'mch_id': [u'指定商户未找到']}
            else:
                has_authed = session.query(AuthMchInfo).filter_by(auth_status=2, mch_id=self.mch_id).count()
                # TODO(leiyutian) 行业是否改变， mch_name是否改变
                mch_inlet_info = session.query(MchInletInfo).filter_by(mch_id=self.mch_id).first()

                if has_authed and self.industry_no and self.industry_no != mch_inlet_info.u_ind_code:
                    content = {'industry_no': [u'无法修改行业信息']}
                if has_authed and self.mch_name and self.mch_name != mch_inlet_info.mch_name:
                    content = {'mch_name': [u'无法修改商户名称']}
                # if has_authed and self.head_name and mch_inlet_info.head_name \
                # and self.head_name != mch_inlet_info.head_name:
                # content = {'head_name': [u'无法修改负责人名称']}
                old_head_name = mch_inlet_info.head_name
                old_head_mobile = mch_inlet_info.head_mobile
                old_img_with_id_card = mch_inlet_info.img_with_id_card
                self.db_mch_inlet_info = mch_inlet_info.to_dict()

                # 如果已经审核通过且是连锁门店，则不能修改所属连锁商户
                if has_authed and self.db_cs_id and self.cs_id != mch_inlet_info.cs_id:
                    content = {'cs_id': [u'无法修改门店所属连锁商户']}
                self.has_authed = has_authed
                db_payments = session.query(MchPayment).filter_by(mch_id=self.mch_id).all()
                for each_payment in db_payments:
                    if each_payment.payment_type in [1, 2, 3, 4, 101, 102, 103]:
                        has_wx_general = True
                    if each_payment.payment_type in [11, 12, 13]:
                        has_wx_dine = True
                if self.has_authed:
                    if has_wx_dine and not self.use_dine:
                        content = {'use_dine': [u'围餐商户在审核通过之后无法修改为非围餐商户']}
                    if has_wx_general and self.use_dine:
                        content = {'use_dine': [u'非围餐商户在审核通过之后无法修改为围餐商户']}
                if self.use_dine:
                    self.extension_info = self.get_db_extensions(session)

        if content:
            raise RESTfulHTTPError(400, content=content)
        self.u_ind_code = self.industry_no
        self.has_wx_dine = has_wx_dine
        if not self.open_dine and self.use_dine:
            self.form.errors['use_dine'] = [u'该平台未开通围餐功能']
            raise RESTfulHTTPError(content=self.form.errors)

        self.use_dine = self.use_dine and self.open_dine

        if self.cs_id and self.use_dine:
            raise RESTfulHTTPError(content={'use_dine': [u'连锁门店无法使用围餐通道']})

        # 如需进件银联，则负责人姓名、电话、手持身份证照片为必传
        if self.form.payment_type33.data is not None or self.form.UNIONPAY_OFFLINE_JSAPI.data is not None:
            error = False
            if not old_img_with_id_card:
                img_with_id_card = self.request.files.get('img_with_id_card')
                if not img_with_id_card:
                    self.form.errors['img'] = [u'必须传入手持身份证照片']
                    error = True
            if not old_head_name and not self.form.head_name.data:
                self.form.errors['head_name'] = [u'必须传入负责人姓名']
                error = True
            if not old_head_mobile and not self.form.head_mobile.data:
                self.form.errors['head_mobile'] = [u'必须传入负责人电话']
                error = True
            if error:
                raise RESTfulHTTPError(content=self.form.errors)

        # 如果本来是连锁门店，就不需要判断支付方式，只需要判断支付费率。
        # 将老的paymnt_type:1,2,3,4 转换成新的 uline_payment_code
        for payment_type in PAY_TYPES:
            payment_rate = self.form.data.get('payment_type' + str(payment_type))
            if payment_rate >= 0:
                setattr(getattr(self.form, old_payment_relations.get(str(payment_type))), 'data', payment_rate)

        # 将老的提现手续费(wx,alipay)转换成新的(wx_draw_fee,ali_draw_fee)
        # 提现手续费
        self.wx_draw_fee = self.ali_draw_fee = None
        if self.form.wx_draw_fee.data:
            self.wx_draw_fee = self.form.wx_draw_fee.data
        elif self.form.wx.data:
            self.wx_draw_fee = self.form.wx.data
        if self.form.ali_draw_fee.data:
            self.ali_draw_fee = self.form.ali_draw_fee.data
        elif self.form.alipay.data:
            self.ali_draw_fee = self.form.alipay.data
        # 提现垫资费
        self.wx_draw_rate = self.form.wx_draw_rate.data
        self.ali_draw_rate = self.form.ali_draw_rate.data

        # 新版的手续费和垫资费，两个都为空或者两个都不为空
        if FEATURE_SWITCH.get('NEW_INLET'):
            if (self.wx_draw_fee and not self.wx_draw_rate):
                self.form.errors['wx_draw_rate'] = [u'微信D0垫资费率不能为空']
            elif (not self.wx_draw_fee and self.wx_draw_rate):
                self.form.errors['wx_draw_fee'] = [u'微信D0代付费用不能为空']
            if (self.ali_draw_fee and not self.ali_draw_rate):
                self.form.errors['ali_draw_rate'] = [u'支付宝D0垫资费率不能为空']
            elif (not self.ali_draw_fee and self.ali_draw_rate):
                self.form.errors['ali_draw_fee'] = [u'支付宝D0代付费用不能为空']

        # 是否传的是老的d0费率，如果是老的费率，涉及到后面拆分（拆成d1费率+d0垫资费）
        self.has_old_wx_d0 = (
                self.form.data.get('payment_type101') is not None or
                self.form.data.get('payment_type102') is not None or
                self.form.data.get('payment_type103') is not None or
                self.form.data.get('payment_type104') is not None or
                self.form.data.get('payment_type105') is not None
              )

        self.has_old_ali_d0 = (
                self.form.data.get('payment_type107') is not None or
                self.form.data.get('payment_type108') is not None or
                self.form.data.get('payment_type109') is not None
              )

        payments = map(lambda x: self.form.data.get(x), new_payment_relations.keys())
        if not self.db_cs_id and not any(x is not None and x >= 0 for x in payments):
            if FEATURE_SWITCH.get('NEW_INLET'):
                self.form.errors['WX_OFFLINE_NATIVE'] = [u'费率不能全部为空且必须大于等于0']
            else:
                self.form.errors['payment_type1'] = [u'费率不能全部为空且必须大于等于0']
            raise RESTfulHTTPError(content=self.form.errors)

        if not self.jd_pay and (
                self.form.data.get('payment_type21') is not None or
                self.form.data.get('payment_type22') is not None or
                self.form.data.get('payment_type23') is not None
              ):
            self.form.errors['payment_type1'] = [u'该银行没有开通京东支付']
            raise RESTfulHTTPError(content=self.form.errors)

        self.has_wx_d1 = (
            self.form.data.get('payment_type1') is not None or
            self.form.data.get('payment_type2') is not None or
            self.form.data.get('payment_type3') is not None or
            self.form.data.get('payment_type4') is not None
        )

        self.add_filed()

        # 判断支付宝M3需要字段
        if not self.cs_id and self.has_ali and MIN_ALI_LEVEL.upper() >= "M3":
            error_info_map = {
                'license_type': ['请填写营业执照类型'],
                'head_mobile': ['请填写负责人电话'],
                'head_name': ['请填写负责人姓名'],
                'district': ['请填写区域信息'],
                'head_type': ['请填写负责人类型'],
            }
            for key, value in error_info_map.iteritems():
                if not self.db_mch_inlet_info.get(key, None) and not getattr(self, key):
                    self.form.errors[key] = value

            if self.form.errors:
                raise RESTfulHTTPError(content=self.form.errors)

        # payments = map(lambda x: self.form.data.get('payment_type' + str(x)), PAY_TYPES)

        # 如果本来是连锁门店，就不需要判断支付方式，只需要判断支付费率。
        # if not self.db_cs_id and not any(x is not None and x >= 0 for x in payments):
        #     self.form.errors['payment_type1'] = [u'费率不能全部为空']
        #     raise RESTfulHTTPError(content=self.form.errors)
        # self.has_wx_d0 = (self.form.data.get('payment_type101') is not None or
        #                   self.form.data.get('payment_type102') is not None or
        #                   self.form.data.get('payment_type103') is not None or
        #                   self.form.data.get('payment_type104') is not None
        #                   )
        # self.has_wx_d1 = (
        #     self.form.data.get('payment_type1') is not None or
        #     self.form.data.get('payment_type2') is not None or
        #     self.form.data.get('payment_type3') is not None or
        #     self.form.data.get('payment_type4') is not None
        # )

        if self.use_dine and (self.has_wx_d0 or self.has_wx_d1):
            raise RESTfulHTTPError(content={'use_dine': ['微信围餐通道无法与普通通道一起使用']})

        if not self.form.validate():
            raise RESTfulHTTPError(400, content=self.form.errors)

        # 相关图片保存
        id_card_img_f_data = self.request.files.get('id_card_img_f')
        id_card_img_b_raw_data = self.request.files.get('id_card_img_b')
        license_img_data = self.request.files.get('license_img')

        if self.form.payment_type33.data is not None or self.form.UNIONPAY_OFFLINE_JSAPI.data is not None:
            img_with_id_card = self.request.files.get('img_with_id_card')
            if img_with_id_card:
                self.img_with_id_card = self.save_idCard_img(img_with_id_card)

        # 删除进件补充材料
        self.save_del_annex_img()

        # 进件补充材料
        annex_imgs = dict()
        for img_count in range(1, 6):
            annex_key = 'annex_img' + str(img_count)
            annex_imgs[annex_key] = self.request.files.get(annex_key, None)

            if annex_imgs[annex_key]:
                img_length = annex_imgs[annex_key][0].get('body').__len__()
                if img_length > 500 * 1024:
                    self.form.errors['img'] = [u'补充材料照片不得大于500Kb']
                    raise RESTfulHTTPError(400, content=self.form.errors)
                # 没有返回说明符合条件，保存图片
                setattr(self, annex_key, self.save_idCard_img(self.request.files.get(annex_key)))
            else:
                # 说明图片为空，保存一个None
                setattr(self, annex_key, None)

            pass

        if id_card_img_f_data:
            if self.request.files['id_card_img_f'][0].body.__len__() > 300 * 1024:
                self.form.errors['id_card_img_f'] = [u'传入照片不得大于300Kb']
                raise RESTfulHTTPError(400, content=self.form.errors)
            img_front_file = self.request.files.get('id_card_img_f')
            self.id_card_img_f = self.save_idCard_img(img_front_file)

        if id_card_img_b_raw_data:
            if self.request.files['id_card_img_b'][0].body.__len__() > 300 * 1024:
                self.form.errors['id_card_img_b'] = [u'传入照片不得大于300Kb']
                raise RESTfulHTTPError(400, content=self.form.errors)
            img_back_file = self.request.files.get('id_card_img_b')
            self.id_card_img_b = self.save_idCard_img(img_back_file)

        if license_img_data:
            if self.request.files['license_img'][0].body.__len__() > 500 * 1024:
                self.form.errors['license_img'] = [u'传入照片不得大于500Kb']
                raise RESTfulHTTPError(400, content=self.form.errors)
            license_img_file = self.request.files.get('license_img')
            self.license_img = self.save_idCard_img(license_img_file)

        if self.use_dine:
            self.save_mch_env_imgs()

        # 存在license_period 则表示长期
        self.license_period = 2 if bool(self.license_period) else 1

        self.license_end_date = None if self.license_period == 2 else self.license_end_date

        self.license_scope = self.form.license_scope.data or ''

        with uline_session_scope() as session:
            try:
                # yield self.update_mch_user(session) uline中没有
                # 首先判断是否是有cs_id，否则，先删掉所有的支付方式，并使用连锁商户的支付方式。
                if self.cs_id:
                    payments = session.query(DtPayment).filter_by(dt_id=self.cs_id).all()
                    if payments:
                        for each_payment in payments:
                            paytype = each_payment.payment_type
                            payment_form = getattr(self.form, 'payment_type' + str(paytype), '')
                            if payment_form:
                                setattr(payment_form, 'data', each_payment.payment_rate)

                        # 将老的paymnt_type:1,2,3,4 转换成新的 uline_payment_code
                        for payment_type in PAY_TYPES:
                            payment_rate = self.form.data.get('payment_type' + str(payment_type))
                            if payment_rate >= 0:
                                setattr(getattr(self.form, old_payment_relations.get(str(payment_type))),
                                        'data', payment_rate)

                # 手续费垫资费也在这里保存到change_dict
                yield self.update_balance_payment(session)
                # if self.alipay is not None or self.wx is not None:
                # yield self.update_d0_withdraw_fee(session)
                # if self.wx_draw_fee is not None or self.ali_draw_fee is not None:
                #     yield self.update_d0_withdraw_fee(session)
                yield self.update_inlet_info(session)
                yield self.add_auth_inlet_info(session)
                self.update_extensions(session)
                self.update_change_record(session)
            except Exception as err:
                session.rollback()
                error_log.exception(err)
                content = getattr(err, 'content', '')
                raise RESTfulHTTPError(500, content=content)
        # if not self.cs_id:
        merchant_info = {
            'id_card_no': self.id_card_no,
            'balance_account': self.balance_account,
            'license_num': self.license_num,
        }
        tornado.gen.Task(query_mch_risk_info.query_merchant_risk_info.apply_async,
                         args=[self.mch_id, 'cs' if self.cs_id else 'mch', merchant_info])
        self.finish({'ul_mchid': self.mch_id})

    def add_filed(self):
        self.has_wx_offline = ''
        self.has_wx_online = ''
        self.has_wx_dine = ''
        self.has_wx_zero = ''

        self.has_wx_d0 = ''
        self.has_wx_d1 = ''

        self.has_ali_offline = ''
        self.has_ali_zero = ''
        self.has_ali_d1 = ''
        self.has_ali_d0 = ''

        self.has_wx = False
        self.has_ali = False

        for payment_type in NEW_AVAILABLE_PAYMENTS.keys():
            payment_rate = getattr(self.form, payment_type).data
            if payment_rate >= 0:
                self.validate_rate = True
                # 支付通道判断
                if payment_type.startswith('WX'):
                    self.has_wx = True
                    # 通道判断
                    if payment_type.startswith('WX_OFFLINE'):
                        self.has_wx_offline = True
                    elif payment_type.startswith('WX_ONLINE'):
                        self.has_wx_online = True
                    elif payment_type.startswith('WX_DINE'):
                        self.has_wx_dine = True
                    elif payment_type.startswith('WX_ZERO'):
                        self.has_wx_zero = True

                    # 结算方式判断
                    if not payment_type.startswith('WX_DINE'):
                        if payment_type.endswith('D0'):
                            self.has_wx_d0 = True
                        else:
                            self.has_wx_d1 = True

                elif payment_type.startswith('ALI'):
                    self.has_ali = True
                    if payment_type.startswith('ALI_OFFLINE'):
                        self.has_ali_offline = True
                    elif payment_type.startswith('ALI_ZERO'):
                        self.has_ali_zero = True
                    if payment_type.endswith('D0'):
                        self.has_ali_d0 = True
                    else:
                        self.has_ali_d1 = True
        if self.wx_draw_fee or self.wx_draw_rate:
            self.has_wx_d0 = True
        if self.ali_draw_fee or self.ali_draw_rate:
            self.has_ali_d0 = True

    def save_del_annex_img(self):
        """
        保存用户需要删除的进件补充材料图片到change_record
        :return:
        """
        del_annex = str(self.form.data.get('del_annex', ""))
        annex_nums = ("1", "2", "3", "4", "5")
        # 移除空格
        del_annex = del_annex.strip()
        if del_annex and isinstance(del_annex, str):
            new_annex = ""
            del_annex_sets = set(del_annex.split("-"))
            for del_set in del_annex_sets:
                # 如果传的图片在范围内就加上
                if del_set in annex_nums:
                    new_annex = new_annex + del_set + "-"
            if new_annex:
                self.change_dict['del_annex'] = new_annex[0:-1]

    def save_del_wx_dine_annex_img(self):
        """保存用户需要删除的微信围餐不从材料图片到change_record"""
        del_wx_dine_annex = str(self.form.data.get('del_wx_dine_annex', "")).strip()
        if del_wx_dine_annex:
            self.change_dict['del_wx_dine_annex'] = [int(index) for index in del_wx_dine_annex.split('-') if
                                                     index and int(index) in range(1, 6)]

    def save_idCard_img(self, imgFile):
        # 不需要根据环境判断存入目录
        if env == 'LOCAL':
            base_dir = os.path.join(
                self.application.base_dir, 'static/uploads/mch/idcard')
        else:
            # 权宜之计,先放到static目录下
            base_dir = os.path.expanduser(
                '~/uline/uline/static/uploads/mch/idcard')
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_name = '{}.jpg'.format(uuid.uuid4().hex)
        file_path = os.path.join(file_dir, file_name)

        try:
            with open(file_path, 'wb') as f:
                f.write(imgFile[0]['body'])
        except Exception as err:
            raise err
        return file_name

    def get_payment_status(self, session, d0=False):
        """
        获取商户费率的开通状态
        :param d0: True代表查询D0的类型，默认False为d1
        :return: 结果大于0代表开通某个类型
        """
        if d0:
            return bool(session.query(MchPayment.mch_id).filter(MchPayment.mch_id == self.mch_id,
                                                                MchPayment.payment_type > 100).count())
        else:
            return bool(session.query(MchPayment.mch_id).filter(MchPayment.mch_id == self.mch_id,
                                                                MchPayment.payment_type < 10).count())

    @tornado.gen.coroutine
    def update_mch_user(self, session):
        # 更新商户
        update_at = datetime.datetime.now()
        mch_user = session.query(MchUser).filter_by(mch_id=self.mch_id).first()
        user_dict = {
            'mch_name': self.mch_name,
            'email': self.email,
            'update_at': update_at,
        }
        self.update_obj(mch_user, user_dict)
        session.flush()

    # 更新实例数据信息
    def update_obj(self, obj, update_info):
        need_update_info = {}
        for k, v in update_info.items():
            if v:
                if not hasattr(obj, k):
                    setattr(obj, k, v)
                    need_update_info[k] = v
                else:
                    obj_v = getattr(obj, k)
                    if obj_v != v:
                        setattr(obj, k, v)
                        need_update_info[k] = v
        return need_update_info

    def get_update_infos(self, obj, update_info):
        need_update_info = {}
        # can_be_none_keys = ['license_type', 'head_name', 'head_mobile']
        for k, v in update_info.items():
            if v or (k == 'license_scope' and v == ''):
                if not hasattr(obj, k):
                    need_update_info[k] = v
                else:
                    obj_v = getattr(obj, k)
                    if obj_v != v:
                        need_update_info[k] = v
        return need_update_info

    @tornado.gen.coroutine
    def update_inlet_info(self, session):
        # 只需要记录更新的记录
        # 添加的商户的基本信息,下一步保存支付信息
        mch_inlet_info = session.query(MchInletInfo).filter_by(mch_id=self.mch_id).first()

        if mch_inlet_info:
            mch_may_update_cols = ['mch_name', 'mch_shortname', 'province', 'city', 'district',
                                   'address', 'contact', 'mobile', 'head_name', 'head_mobile',
                                   'service_phone', 'email',
                                   'license_num', 'license_start_date', 'license_end_date',
                                   'license_period', 'license_scope', 'notify_url', 'dt_sub_id', 'u_ind_code', 'cs_id',
                                   'annex_img1', 'annex_img2', 'annex_img3', 'annex_img4', 'annex_img5', 'del_annex',
                                   'img_with_id_card', 'license_type', 'head_type'
                                   ]
            for field in ['id_card_img_f', 'id_card_img_b', 'license_img']:
                if isinstance(getattr(self, field), str):
                    mch_may_update_cols.append(field)

            update_info = self.get_update_dict(mch_may_update_cols)
            need_update_info = self.get_update_infos(mch_inlet_info, update_info)
            province_keys = ['province', 'city']
            for key in province_keys:
                if key in need_update_info:
                    value = need_update_info[key]
                    if '-' in value:
                        need_update_info[key] = value[value.index('-') + 1:]
                    else:
                        need_update_info[key] = value
            if need_update_info:
                self.change_dict.update(need_update_info)

                # 如果有修改，则需要更新状态未待审核
                # if self.change_dict:
                # 营业执照结束时期
                # if self.license_period == 1:
                #     setattr(mch_inlet_info, 'license_end_date', self.license_end_date)
                # if self.license_period == 2:
                #     setattr(mch_inlet_info, 'license_end_date', None)
            # if need_update_info:
            self.change_dict['pre_auth_status'] = mch_inlet_info.auth_status
            changed_u_ind_code = self.change_dict.get('u_ind_code', '')
            self.update_changed_industry_info(session, changed_u_ind_code)
            setattr(mch_inlet_info, 'auth_status', 1)
            setattr(mch_inlet_info, 'update_at', self.update_at)
            session.flush()

    def update_changed_industry_info(self, session, changed_u_ind_code):
        if changed_u_ind_code:
            industry_info = session.query(UlineIndustryInfo).filter_by(industry_code=changed_u_ind_code).first()
            if industry_info:
                self.change_dict['u_ind_name'] = industry_info.industry_name
                wx_ind_code = industry_info.wx_ind_code
                self.change_dict['wx_ind_code'] = industry_info.wx_ind_code
                wx_ind_info = session.query(UlineIndustryInfo).filter_by(wx_ind_code=wx_ind_code, status=2).first()
                self.change_dict['wx_ind_name'] = wx_ind_info.industry_name if wx_ind_info else ''

                new_ali_ind_code = industry_info.new_ali_ind_code
                self.change_dict['ali_ind_code'] = new_ali_ind_code
                ali_ind_info = session.query(IndustryAliInfo).filter_by(industry_code=new_ali_ind_code).first()
                self.change_dict['ali_ind_name'] = ali_ind_info.industry_name if ali_ind_info else ''

                jd_ind_code = industry_info.jd_ind_code
                self.change_dict['jd_ind_code'] = jd_ind_code
                jd_ind_info = session.query(IndustryJDInfo).filter_by(industry_code=jd_ind_code).first()
                self.change_dict['jd_ind_name'] = jd_ind_info.industry_name if jd_ind_info else ''

    @tornado.gen.coroutine
    def update_d0_withdraw_fee(self, session):
        wx_draw_fee = int(self.wx_draw_fee) if self.wx_draw_fee else None
        ali_draw_fee = int(self.ali_draw_fee) if self.ali_draw_fee else None

        wx_draw_rate = int(self.wx_draw_rate) if self.wx_draw_rate else None
        ali_draw_rate = int(self.ali_draw_rate) if self.ali_draw_rate else None

        d0_fee = session.query(D0WithdrawPay).filter_by(role=self.mch_id, role_type='mch').first()
        if d0_fee:
            self.change_dict['role'] = {'wx_draw_fee': wx_draw_fee, 'ali_draw_fee': ali_draw_fee,
                                        'wx_draw_rate': wx_draw_rate, 'ali_draw_rate': ali_draw_rate,
                                        'action_type': 2}
        else:
            self.change_dict['role'] = {'wx_draw_fee': wx_draw_fee, 'ali_draw_fee': ali_draw_fee,
                                        'wx_draw_rate': wx_draw_rate, 'ali_draw_rate': ali_draw_rate,
                                        'action_type': 1}

    @tornado.gen.coroutine
    def update_balance_payment(self, session):
        """更新商户的支付方式.
        关于更新支付方式有连锁门店和普通商户。
        db     form      change_record记录的动作
        ------------------------------
        有       有        更新操作
        没有     有        新增操作
        普通商户：
        有       没有      无操作
        连锁门店：
        有       没有      删除原有操作
        """
        # 商户结算账户表(mch_balance)
        # 商户支付方式表(mch_payment)
        balance = session.query(
            MchBalance).filter_by(mch_id=self.mch_id).first()
        if balance:
            balance_update_need_cols = ['balance_type', 'balance_name', 'bank_no', 'balance_account',
                                        'id_card_no', 'update_at']
            data = self.get_update_dict(balance_update_need_cols)
            balance_update_info = self.get_update_infos(balance, data)
            self.change_dict['balance_info'] = balance_update_info
            # 支持多种支付类型 万分率
            # 转变成[[payment_type,payment_rate]] for循环
            # db_payments = self.get_mch_payments(session)
            db_payments = self.get_new_mch_payments(session)
            if 'payment' not in self.change_dict:
                self.change_dict['payment'] = dict()
            db_paytype = []
            # 尝试去数据库中查找是否存在，因为修改的时候，可能不传
            if not self.wx_draw_fee:
                self.wx_draw_fee = self.get_mch_withdraw_rate(session, 'WX')
            if not self.ali_draw_fee:
                self.ali_draw_fee = self.get_mch_withdraw_rate(session, 'ALI')
            # for payment_type in AVAILABLE_PAYMENTS.keys():
            for payment_type in NEW_AVAILABLE_PAYMENTS.keys():
                # payment_rate = getattr(self, 'payment_type' + str(payment_type), None)
                payment_rate = getattr(self, payment_type, None)
                if payment_rate is not None and payment_rate >= 0:
                    data = {}
                    error_log.exception(' self.wx_draw_fee:%s' % self.wx_draw_fee)
                    if payment_type.find('WX') != -1 and self.wx_draw_fee:
                        data['withdraw_fee'] = self.wx_draw_fee
                        if FEATURE_SWITCH.get('NEW_INLET'):
                            if self.wx_draw_rate:
                                data['withdraw_rate'] = self.wx_draw_rate
                            else:
                                withdraw_rate = self.get_dt_withdraw_rate(session, 'WX')
                                error_log.exception(' withdraw_rate:%s' % withdraw_rate)
                                if withdraw_rate:
                                    data['withdraw_rate'] = withdraw_rate
                                    error_log.exception(' data[withdraw_rate]:%s' % data['withdraw_rate'])
                    if payment_type.find('ALI') != -1 and self.ali_draw_fee:
                        data['withdraw_fee'] = self.ali_draw_fee
                        if FEATURE_SWITCH.get('NEW_INLET'):
                            if self.ali_draw_rate:
                                data['withdraw_rate'] = self.ali_draw_rate
                            else:
                                withdraw_rate = self.get_dt_withdraw_rate(session, 'ALI')
                                if withdraw_rate:
                                    data['withdraw_rate'] = withdraw_rate

                    # 保存到self.role中
                    if FEATURE_SWITCH.get('NEW_INLET') and data.get('withdraw_rate') and data.get('withdraw_fee'):
                        if self.change_dict.get('role') is None:
                            self.change_dict['role'] = {}
                        if payment_type.find('WX') != -1:
                            self.change_dict['role']['wx_draw_fee'] = str(data.get('withdraw_fee'))
                            self.change_dict['role']['wx_draw_rate'] = str(data.get('withdraw_rate'))
                        elif payment_type.find('ALI') != -1:
                            self.change_dict['role']['ali_draw_fee'] = str(data.get('withdraw_fee'))
                            self.change_dict['role']['ali_draw_rate'] = str(data.get('withdraw_rate'))
                    error_log.exception(' self.change_dict:%s' % self.change_dict.get('role'))

                    # mch_payment = db_payments.get(int(payment_type), None)
                    is_d0 = False
                    if payment_type.endswith('D0'):
                        is_d0 = True
                        payment_type = payment_type[:-3]
                    mch_payment = db_payments.get(payment_type)
                    if mch_payment:
                        # db_paytype.append(int(payment_type))
                        db_paytype.append(payment_type)

                    # 如果支付方式的费率没变，则不需要存储uline/templates/merchant/inlet/merchant.html
                    if mch_payment and mch_payment.payment_rate == int(payment_rate):
                        continue

                    # 原有的没有
                    if not mch_payment:
                        update_info = {
                            'pay_type': payment_type,
                            'pay_rate': int(payment_rate),
                            'pre_status': 1,
                            'activated_status': 1,
                            'action_type': 1,  # 1为新增 2为更新 3为删除
                            'after_auth_status': 2,  # 审核通过之后的状态
                        }
                        if FEATURE_SWITCH.get('NEW_INLET') and data.get('withdraw_rate') is not None \
                                and is_d0 and (self.has_old_wx_d0 or self.has_old_ali_d0):
                            update_info['pay_rate'] -= data.get('withdraw_rate')
                            update_info['settle_rate'] = update_info['pay_rate']

                        self.change_dict['payment'][payment_type] = update_info
                        # mch_payment = MchPayment(**data)
                        # session.add(mch_payment)
                    # 需要修改
                    else:
                        # 添加变更记录信息
                        # 如果没有发生改变，则保持原有状态不变
                        db_active_status = mch_payment.activated_status
                        if mch_payment.activated_status == 1:
                            # 如果之前状态为未激活,就应该保持为未激活
                            change_status = 1
                        else:
                            change_status = 3 if payment_rate != mch_payment.payment_rate else db_active_status

                        # after_auth_status = 1 if payment_rate != mch_payment.payment_rate else db_active_status

                        # 如果有修改则存储修改记录
                        if payment_rate != mch_payment.payment_rate:
                            update_info = {
                                'pay_type': payment_type,
                                'pay_rate': int(payment_rate),
                                'pre_status': mch_payment.activated_status,
                                'activated_status': change_status,
                                'action_type': 2,  # 1为新增 2为更新 3为删除
                                'after_auth_status': mch_payment.activated_status,
                            }

                            if FEATURE_SWITCH.get('NEW_INLET') and data.get('withdraw_rate') is not None and is_d0:
                                update_info['pay_rate'] -= data.get('withdraw_rate')
                                update_info['settle_rate'] = update_info['pay_rate']

                            self.change_dict['payment'][payment_type] = update_info

                            # 如果是
                            # data = {
                            #     'activated_status': change_status,
                            #     'update_at': self.update_at
                            # }
                            # self.update_obj(mch_payment, data)
                            # db_paytype.append(payment_type)

            # 如果是原来是连锁商户且与现有的不同, 则需要完全删除原有的不同支付方式。
            to_delete_types = [paytype for paytype in db_payments.keys() if paytype not in db_paytype]
            for each_type in to_delete_types:
                payment = db_payments[each_type]
                uline_payment_code = old_payment_relations.get(str(payment.payment_type))
                update_info = {
                    'pay_type': uline_payment_code,
                    'pay_rate': int(payment.payment_rate),
                    'pre_status': payment.activated_status,
                    'activated_status': payment.activated_status,
                    'action_type': 3,
                }
                self.change_dict['payment'][uline_payment_code] = update_info
            session.flush()

    @tornado.gen.coroutine
    def add_auth_inlet_info(self, session):
        data = {
            'mch_id': self.mch_id,
            'comment': u'提交修改',
            'auth_user': session.query(DtUser).filter_by(
                dt_id=self.dt_id).first().dt_name,
            'auth_status': 1,
            'create_at': datetime.datetime.now()
        }
        auth_info = AuthMchInfo(**data)
        session.add(auth_info)
        session.flush()

    def get_update_dict(self, need_cols):
        update_infos = dict()
        for each_col in need_cols:
            try:
                update_infos[each_col] = getattr(self, each_col, None)
            except AttributeError:
                print 'no column {}'.format(each_col)
        return update_infos

    def get_dt_withdraw_rate(self, session, type):
        try:
            return session.query(DtPayment).filter(DtPayment.uline_payment_code.startswith(type),
                                                   DtPayment.dt_id == self.dt_id).first().withdraw_rate
        except Exception:
            return None

    def get_mch_withdraw_rate(self, session, type):
        try:
            return session.query(MchPayment).filter(MchPayment.uline_payment_code.startswith(type),
                                                    MchPayment.mch_id == self.mch_id).first().withdraw_fee
        except Exception:
            return None

    def update_change_record(self, session):
        record = session.query(ChangeRecord).filter_by(mch_id=self.mch_id, status=1).first()
        change_json_data = json.dumps(self.change_dict, cls=ComplexEncoder)
        if not record:
            data = {
                'mch_id': self.mch_id,
                'data_json': change_json_data,
                'change_type': 2,
                'status': 1,
                'create_at': self.update_at
            }
            change_record = ChangeRecord(**data)
            session.add(change_record)
        else:
            record.status = 1
            record.create_at = self.update_at
            record.data_json = change_json_data
        session.flush()

    def get_mch_payments(self, session):
        payments = dict()
        mch_payments = session.query(MchPayment).filter(MchPayment.mch_id == self.mch_id).all()
        for each_mch_payment in mch_payments:
            payments[each_mch_payment.payment_type] = each_mch_payment
        return payments

    def get_new_mch_payments(self, session):
        payments = dict()
        mch_payments = session.query(MchPayment).filter(MchPayment.mch_id == self.mch_id).all()
        for each_mch_payment in mch_payments:
            # 表示d0
            # if each_mch_payment.uline_settle_id == 2:
            #     payments[each_mch_payment.uline_payment_code + '_D0'] = each_mch_payment
            # else:
            payments[each_mch_payment.uline_payment_code] = each_mch_payment
        return payments

    def save_mch_env_imgs(self):
        mch_env_imgs = {
            'mch_desk_img': '必须传入商户收银台照片',
            'mch_inner_img': '必须传入商户内部环境照片',
            'mch_front_img': '必须传入商户门店门口照片'
        }
        mch_env_img_exist = {key: self.extension_info[key] for key in self.extension_info if key in mch_env_imgs}

        for each_img in mch_env_imgs:
            if self.save_img(each_img, 500):
                mch_env_img_exist[each_img] = True
        lack_env_img = [each_img for each_img in mch_env_imgs if each_img not in mch_env_img_exist]
        content = {each_img: [mch_env_imgs[each_img]] for each_img in lack_env_img}

        has_update_dine_img = False
        for img_index in range(1, 6):
            has_img_data = self.save_img('wx_dine_annex_img' + str(img_index), 500)
            if not has_update_dine_img:
                has_update_dine_img = has_img_data

        self.save_del_wx_dine_annex_img()
        # 只要是围餐商户，不管是原来是不是围餐商户，都需要判断修改后是否会存在围餐补充材料
        if not has_update_dine_img:
            del_dine_annex_indexs = self.change_dict.get('del_wx_dine_annex', [])
            rest_extension_name = [key for key in self.extension_info if
                                   key not in ['wx_dine_annex_img' + str(index) for index in del_dine_annex_indexs] and
                                   'wx_dine_annex_img' in key]
            if not rest_extension_name:
                content.update({'wx_dine_annex_img1': [u'必须传入围餐补充材料']})
        if content:
            raise RESTfulHTTPError(400, content=content)

    def save_img(self, field_name, max_size, default_key_name=''):
        img_data = self.request.files.get(field_name)
        has_data = False
        if img_data:
            if self.request.files[field_name][0].body.__len__() > max_size * 1024:
                self.form.errors[field_name] = [u'传入的{}照片不得大于{}Kb'.format(default_key_name, max_size)]
                raise RESTfulHTTPError(400, content=self.form.errors)
            img_file = self.request.files.get(field_name)
            file_name = self.save_idCard_img(img_file)
            setattr(self, field_name, file_name)
            has_data = True
        else:
            setattr(self, field_name, None)
        return has_data

    def update_extensions(self, session):
        if self.use_dine:
            extension_names = ['mch_desk_img', 'mch_inner_img', 'mch_front_img']
            extension_names.extend(['wx_dine_annex_img{}'.format(i) for i in range(1, 6)])
            for extension_name in extension_names:
                extensions_db = session.query(RoleExtensionInfos).filter(
                        RoleExtensionInfos.role_id == self.mch_id,
                        RoleExtensionInfos.role_type == 'mch',
                        RoleExtensionInfos.extension_name == extension_name).first()
                update_extension = getattr(self, extension_name, None)
                if update_extension and (not extensions_db or update_extension != extensions_db.extension_value):
                    self.change_dict[extension_name] = update_extension

    def get_db_extensions(self, session):
        extensions_db = session.query(RoleExtensionInfos).filter(RoleExtensionInfos.role_id == self.mch_id,
                                                                 RoleExtensionInfos.role_type == 'mch').all()
        extension_map = {each_extension.extension_name: each_extension.extension_value for each_extension in
                         extensions_db}
        return extension_map


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)
