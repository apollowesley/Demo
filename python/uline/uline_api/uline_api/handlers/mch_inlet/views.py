# -*- coding: utf-8 -*-

import datetime
import random
import uuid

import os
import tornado.escape
import tornado.gen
import tornado.web

from uline_api.handlers.baseHandlers import RESTfulHandler, RESTfulHTTPError
from uline_api.model.uline.info import (
    MchInletInfo, MchBalance, MchPayment, UlineIndustryInfo, D0WithdrawPay, DtPayment, RoleExtensionInfos,UserProfile,EmployeeUserLog,
UlinePayment)
from sqlalchemy.sql import func
from uline_api.model.uline.other import AuthMchInfo
from uline_api.model.uline.user import MchUser, DtUser
from uline_api.model.uline.other import AuthMchInfo,SysType
from uline_api.model.uline.user import MchUser, DtUser,Employee
from uline_api.public.constants import translate_payment_type, old_payment_relations, new_payment_relations, \
    NEW_AVAILABLE_PAYMENTS

from uline_api.model.uline.info import DtInletInfo
from uline_api.model.uline.permit import EmployeeRolePermit,Role
from uline_api.setting import PAY_TYPES, FEATURE_SWITCH, DINE_PAY_TYPES
from uline_api.setting import env
from uline_api.settings import MIN_ALI_LEVEL

from uline_api.util import common
from uline_api.util.db import uline_session_scope
from uline_api.util.log import error_log
from .form import AddMerchantlnlet
from uline.backend.risk import query_mch_risk_info


def create_mch_id():
    with uline_session_scope() as session:
        incr_id = session.execute("select nextval('tb_mch_id_seq')").scalar()
        mch_id = int(str(incr_id) + str(random.randint(10, 99)))
        return mch_id


class AddMerchant(RESTfulHandler, AddMerchantlnlet):
    def prepare(self):
        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER', False)
        self.jd_pay = FEATURE_SWITCH.get('JD_PAY')
        use_dine = self.request.arguments.get('use_dine', [''])[0]
        if self.open_dine and use_dine:
            for each_paytype in DINE_PAY_TYPES:
                self.request.arguments['payment_type' + str(each_paytype)] = ['0']

        if self.request.method == 'POST':
            super(AddMerchant, self).prepare()
            cs_id = self.get_arguments('cs_id')
            if cs_id and cs_id[0]:
                for payment_type in PAY_TYPES:
                    field_name = u'payment_type' + str(payment_type)
                    if field_name in self.request.arguments:
                        del self.request.arguments[u'payment_type' + str(payment_type)]
            self.form = AddMerchantlnlet(self)
            setattr(self.form, 'dt_id', self.dt_id)

    @tornado.gen.coroutine
    def post(self):
        self.mch_id = create_mch_id()
        if not self.open_dine and self.use_dine:
            self.form.errors['use_dine'] = [u'该平台未开通围餐功能']
            raise RESTfulHTTPError(content=self.form.errors)

        self.use_dine = self.use_dine and self.open_dine

        if self.cs_id and self.use_dine:
            raise RESTfulHTTPError(content={'use_dine': [u'连锁门店无法使用围餐通道']})

        self.form.id_card_img_f.raw_data = self.request.files.get(
            'id_card_img_f')
        self.form.id_card_img_b.raw_data = self.request.files.get(
            'id_card_img_b')
        self.form.license_img.raw_data = self.request.files.get(
            'license_img')
        self.form.img_with_id_card.raw_data = self.request.files.get(
            'img_with_id_card')

        # 进件补充材料
        self.form.annex_img1.raw_data = self.request.files.get('annex_img1', None)
        self.form.annex_img2.raw_data = self.request.files.get('annex_img2', None)
        self.form.annex_img3.raw_data = self.request.files.get('annex_img3', None)
        self.form.annex_img4.raw_data = self.request.files.get('annex_img4', None)
        self.form.annex_img5.raw_data = self.request.files.get('annex_img5', None)

        for i in range(1, 6):
            data_key = 'wx_dine_annex_img' + str(i)
            setattr(getattr(self.form, data_key), 'raw_data', self.request.files.get(data_key, None))

        if (self.form.id_card_img_f.raw_data is None) or (
                    self.form.id_card_img_b.raw_data is None) or (
                    self.form.license_img.raw_data is None):
            self.form.errors['img'] = [u'必须传入照片']
            raise RESTfulHTTPError(content=self.form.errors)
        if self.request.files['id_card_img_f'][0].body.__len__() > 300 * 1024 or \
           self.request.files['id_card_img_b'][0].body.__len__() > 300 * 1024 or \
           self.request.files['license_img'][0].body.__len__() > 500 * 1024:
                self.form.errors['img'] = [u'传入照片不得大于300Kb或者500Kb']
                raise RESTfulHTTPError(content=self.form.errors)
        # 如需进件银联，则负责人姓名、电话、手持身份证照片为必传
        if self.form.payment_type33.data is not None:
            if not self.form.img_with_id_card.raw_data:
                self.form.errors['img'] = [u'必须传入手持身份证照片']
            if not self.form.head_name.data:
                self.form.errors['head_name'] = [u'必须传入负责人姓名']
            if not self.form.head_mobile.data:
                self.form.errors['head_mobile'] = [u'必须传入负责人电话']
            if self.form.errors:
                raise RESTfulHTTPError(content=self.form.errors)

        # 围餐商户图片判断
        if self.use_dine:
            self.form.mch_front_img.raw_data = self.request.files.get('mch_front_img', None)
            self.form.mch_desk_img.raw_data = self.request.files.get('mch_desk_img', None)
            self.form.mch_inner_img.raw_data = self.request.files.get('mch_inner_img', None)
            if (self.form.mch_desk_img.raw_data is None):
                self.form.errors['mch_desk_img'] = [u'必须传入商户收银台照片']
                raise RESTfulHTTPError(content=self.form.errors)
            if self.form.mch_inner_img.raw_data is None:
                self.form.errors['mch_inner_img'] = [u'必须传入商户内部环境照片']
                raise RESTfulHTTPError(content=self.form.errors)
            if self.form.mch_front_img.raw_data is None:
                self.form.errors['mch_front_img'] = [u'必须传入商户门店门口照片']
                raise RESTfulHTTPError(content=self.form.errors)

            if (
                self.request.files['mch_front_img'][0].body.__len__() > 500 * 1024 or
                self.request.files['mch_desk_img'][0].body.__len__() > 500 * 1024 or
                self.request.files['mch_inner_img'][0].body.__len__() > 500 * 1024
               ):
                self.form.errors['img'] = [u'传入围餐商户的门店照片不得大于500Kb']
                raise RESTfulHTTPError(content=self.form.errors)
            has_dine_imgs = self.check_dine_img()
            if not has_dine_imgs:
                self.form.errors['dine_annex_img'] = [u'围餐商户必须传入至少一张围餐补充材料图片']
                raise RESTfulHTTPError(content=self.form.errors)
        else:
            self.clean_dine_infos()  # 如果有cs_id，则使用连锁商户的支付方式

        # 如果是连锁商户,则添加
        if self.cs_id:
            for payment_type in PAY_TYPES:
                getattr(self.form, 'payment_type' + str(payment_type)).data = None

            with uline_session_scope() as session:
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

        payments = map(lambda x: self.form.data.get(x), new_payment_relations.keys())
        if not any(x is not None and x >= 0 for x in payments):
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

        self.has_wx_d0 = (self.form.data.get('payment_type101') is not None or
                          self.form.data.get('payment_type102') is not None or
                          self.form.data.get('payment_type103') is not None or
                          self.form.data.get('payment_type104') is not None or
                          self.form.data.get('payment_type105') is not None
                          )
        self.has_wx_d1 = (
            self.form.data.get('payment_type1') is not None or
            self.form.data.get('payment_type2') is not None or
            self.form.data.get('payment_type3') is not None or
            self.form.data.get('payment_type4') is not None or
            self.form.data.get('payment_type5') is not None
        )

        if self.use_dine and (self.has_wx_d0 or self.has_wx_d1):
            raise RESTfulHTTPError(content={'use_dine': ['微信围餐无法与普通通道一起使用']})

        self.add_filed()

        if not self.cs_id and self.has_ali and MIN_ALI_LEVEL.upper() >= "M3":
            error_info_map = {
                'license_type': ['使用支付宝需填写营业执照类型'],
                'head_mobile': ['请填写负责人电话'],
                'head_name': ['请填写负责人姓名'],
                'district': ['请填写区域信息'],
                'head_type': ['请填写负责人类型'],
            }
            for key, value in error_info_map.iteritems():
                if not getattr(self, key):
                    self.form.errors[key] = value

            if self.form.errors:
                raise RESTfulHTTPError(content=self.form.errors)

        if FEATURE_SWITCH.get('NEW_INLET'):
            # 如果有d0费率，则必须填手续费
            if self.has_wx_d0 and not self.wx_draw_fee:
                self.form.errors['wx_draw_fee'] = [u'开通微信D0时，此字段必填']
                raise RESTfulHTTPError(content=self.form.errors)
            if self.has_ali_d0 and not self.ali_draw_fee:
                self.form.errors['ali_draw_fee'] = [u'开通微信D0时，此字段必填']
                raise RESTfulHTTPError(content=self.form.errors)

        # self.has_wx_d0 = (self.form.data.get('WX_OFFLINE_NATIVE_D0') is not None or
        #                   self.form.data.get('WX_OFFLINE_MICROPAY_D0') is not None or
        #                   self.form.data.get('WX_OFFLINE_JSAPI_D0') is not None or
        #                   self.form.data.get('WX_ONLINE_NATIVE_D0') is not None or
        #                   self.form.data.get('WX_ONLINE_JSAPI_D0') is not None or
        #                   self.form.data.get('WX_ONLINE_APP_D0') is not None or
        #                   self.form.data.get('WX_ONLINE_MWEB_D0') is not None
        #                   )
        # self.has_wx_d1 = (
        #     self.form.data.get('WX_OFFLINE_NATIVE') is not None or
        #     self.form.data.get('WX_OFFLINE_MICROPAY') is not None or
        #     self.form.data.get('WX_OFFLINE_JSAPI') is not None or
        #     self.form.data.get('WX_ONLINE_NATIVE') is not None or
        #     self.form.data.get('WX_ONLINE_JSAPI') is not None or
        #     self.form.data.get('WX_ONLINE_APP') is not None or
        #     self.form.data.get('WX_ONLINE_MWEB') is not None
        # )

        # if self.use_dine and (self.has_wx_d0 or self.has_wx_d1):
        #     raise RESTfulHTTPError(content={'use_dine': ['微信围餐无法与普通通道一起使用']})

        # payments = map(lambda x: self.form.data.get('payment_type' + str(x)), PAY_TYPES)
        # if not any(x is not None and x >= 0 for x in payments):
        #     self.form.errors['payment_type1'] = [u'费率不能全部为空且必须大于等于0']
        #     raise RESTfulHTTPError(content=self.form.errors)
        #
        # self.has_wx_d0 = (self.form.data.get('payment_type101') is not None or
        #                   self.form.data.get('payment_type102') is not None or
        #                   self.form.data.get('payment_type103') is not None or
        #                   self.form.data.get('payment_type104') is not None or
        #                   self.form.data.get('payment_type105') is not None
        #                   )
        # self.has_wx_d1 = (
        #     self.form.data.get('payment_type1') is not None or
        #     self.form.data.get('payment_type2') is not None or
        #     self.form.data.get('payment_type3') is not None or
        #     self.form.data.get('payment_type4') is not None or
        #     self.form.data.get('payment_type5') is not None
        # )
        #
        # if self.use_dine and (self.has_wx_d0 or self.has_wx_d1):
        #     raise RESTfulHTTPError(content={'use_dine': ['微信围餐无法与普通通道一起使用']})

        if not self.form.validate():
            raise RESTfulHTTPError(content=self.form.errors)

        # if (
        #     self.form.data.get('payment_type101') is not None or
        #     self.form.data.get('payment_type102') is not None or
        #     self.form.data.get('payment_type103') is not None or
        #     self.form.data.get('payment_type104') is not None or
        #     self.form.data.get('payment_type105') is not None
        # ) and self.form.data.get('wx') is None:
        if self.has_wx_d0 and (self.form.data.get('wx') is None and self.form.data.get('wx_draw_fee')):
            self.form.errors['wx'] = [u'D0微信提现手续费不能为空']
            raise RESTfulHTTPError(content=self.form.errors)

        # if (
        #     self.form.data.get('checkItem107') is not None or
        #     self.form.data.get('checkItem108') is not None or
        #     self.form.data.get('checkItem109') is not None
        # ) and self.form.data.get('alipay') is None:
        if self.has_ali_d0 and (self.form.data.get('alipay') is None and self.form.data.get('ali_draw_fee')):
            self.form.errors['alipay'] = [u'D0支付宝提现手续费不能为空']
            raise RESTfulHTTPError(content=self.form.errors)

        # 进件补充材料
        for img_count in range(1, 6):
            img_name = 'annex_img' + str(img_count)
            annex_img_data = getattr(self.form, img_name).raw_data
            # 如果不为None
            if annex_img_data:
                img_length = annex_img_data[0].get('body').__len__()
                if img_length > 500 * 1024:
                    self.form.errors['img'] = [u'补充材料照片不得大于500Kb']
                    raise RESTfulHTTPError(content=self.form.errors)

                # 没有返回说明符合条件，保存图片
                setattr(self, img_name, self.save_idCard_img(self.request.files.get(img_name)))
            else:
                # 说明图片为空，保存一个None
                setattr(self, img_name, None)

        # 存在license_period 则表示长期
        self.license_period = 2 if bool(self.license_period) else 1

        self.license_end_date = None if self.license_period == 2 else self.license_end_date

        imgFrontFile = self.request.files.get('id_card_img_f')
        imgBackFile = self.request.files.get('id_card_img_b')
        licenceImgFile = self.request.files.get('license_img')

        self.id_card_img_f = self.save_idCard_img(imgFrontFile)
        self.id_card_img_b = self.save_idCard_img(imgBackFile)
        self.license_img = self.save_idCard_img(licenceImgFile)

        if self.form.payment_type33.data is not None:
            img_with_id_card = self.request.files.get('img_with_id_card')
            self.img_with_id_card = self.save_idCard_img(img_with_id_card)

        if self.use_dine:
            img_mch_front = self.request.files.get('mch_front_img')
            img_mch_inner = self.request.files.get('mch_inner_img')
            img_mch_desk = self.request.files.get('mch_desk_img')
            self.mch_front_img = self.save_idCard_img(img_mch_front)
            self.mch_inner_img = self.save_idCard_img(img_mch_inner)
            self.mch_desk_img = self.save_idCard_img(img_mch_desk)

        with uline_session_scope() as session:
            try:
                yield self.add_mch_user(session)
                self.update_inlet_info(session)
                self.update_balance_payment(session)
                self.add_auth_inlet_info(session)
                self.update_employee_profile(session)
                if self.wx_draw_fee is not None or self.ali_draw_fee is not None:
                    self.add_d0_withdraw_fee(session)
            except Exception as err:
                session.rollback()
                error_log.exception(err)
                raise RESTfulHTTPError(500)
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

        self.has_ali = False
        self.has_wx = False

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

    def clean_dine_infos(self):
        # 清空围餐信息数据
        for img_count in range(1, 6):
            img_name = 'wx_dine_annex_img' + str(img_count)
            setattr(self, img_name, None)

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

        with open(file_path, 'wb') as f:
            f.write(imgFile[0]['body'])
        return file_name

    @tornado.gen.coroutine
    def add_mch_user(self, session):
        # 新建一个商户,默认密码123456
        self._password = yield common.bcrypt_pwd(str(self.mobile))
        self.mch_pay_key = os.urandom(16).encode('hex').upper()
        create_at = update_at = datetime.datetime.now()

        user = {
            'mch_id': self.mch_id,
            'mch_name': self.mch_name,
            'email': self.email,
            'password': self._password,
            'create_at': create_at,
            'update_at': update_at,
            'mch_pay_key': self.mch_pay_key,
            # 'wx_sub_mch_id': self.wx_sub_mch_id,
            'status': 1  # 创建
        }
        mch_user = MchUser(**user)

        # 添加是否使用渠道商appid字段
        if self.wx_use_parent in [2, '2']:
            mch_user.wx_use_parent = self.wx_use_parent
        else:
            mch_user.wx_use_parent = 1

        session.add(mch_user)

    def update_inlet_info(self, session):
        # 添加的商户的基本信息,下一步保存支付信息
        create_at = update_at = datetime.datetime.now()
        wx_ind_code, ali_ind_code, jd_ind_code = UlineIndustryInfo.get_wx_ali_jd_code(
            self.industry_no)

        # 增加同业银行id
        dt_user = DtInletInfo.get_by(dt_id=self.dt_id).first()
        bk_id = dt_user.bk_id
        activate_email_tag = self.activate_email_tag if self.activate_email_tag else 1
        data = {
            "mch_id": self.mch_id,
            'mch_name': self.mch_name,
            'mch_shortname': self.mch_shortname,
            'dt_id': self.dt_id,
            'dt_sub_id': self.dt_sub_id,
            'u_ind_code': self.industry_no,
            'wx_ind_code': wx_ind_code,
            'ali_ind_code': ali_ind_code,
            'jd_ind_code': jd_ind_code,
            'province': self.province,
            'city': self.city,
            'district': self.district,
            'address': self.address,
            'contact': self.contact,
            'mobile': self.mobile,
            'service_phone': self.service_phone,
            'email': self.email,
            'id_card_img_f': self.id_card_img_f,
            'id_card_img_b': self.id_card_img_b,
            'annex_img1': self.annex_img1,
            'annex_img2': self.annex_img2,
            'annex_img3': self.annex_img3,
            'annex_img4': self.annex_img4,
            'annex_img5': self.annex_img5,
            'auth_status': 1,
            'activated_status': 1,
            'create_at': create_at,
            'update_at': update_at,
            'license_num': self.license_num,
            'license_start_date': self.license_start_date,
            'license_end_date': self.license_end_date,
            'license_period': self.license_period,
            'license_scope': self.license_scope,
            'license_img': self.license_img,
            'cs_id': self.cs_id,
            'bk_id': bk_id,
            # 银联
            'head_name': self.head_name,
            'head_mobile': self.head_mobile,
            'img_with_id_card': self.img_with_id_card,
            'activate_email_tag': activate_email_tag,
            'license_type': self.license_type,
            'head_type': self.head_type,
        }
        if self.notify_url:
            data['notify_url'] = self.notify_url
        mch_user = MchInletInfo(**data)
        session.add(mch_user)

        dine_extensions = ['mch_front_img', 'mch_desk_img', 'mch_inner_img']
        dine_extensions.extend(['wx_dine_annex_img' + str(index) for index in range(1, 6)])
        for each_key in dine_extensions:
            extension_value = getattr(self, each_key, None)
            create_at = update_at = datetime.datetime.now()
            if extension_value:
                data = {
                    'role_id': self.mch_id,
                    'role_type': 'mch',
                    'extension_name': each_key,
                    'extension_value': extension_value,
                    'create_time': create_at,
                    'update_time': update_at
                }
                extension_info = RoleExtensionInfos(**data)
                session.add(extension_info)

    def update_balance_payment(self, session):
        # 商户结算账户表(mch_balance)
        # 商户支付方式表(mch_payment)
        balance = {
            'mch_id': self.mch_id,
            'balance_type': self.balance_type,
            'balance_name': self.balance_name,
            'bank_no': self.bank_no,
            'balance_account': self.balance_account,
            'id_card_no': self.id_card_no,
            'create_at': datetime.datetime.now(),
            'update_at': datetime.datetime.now()
        }
        mch_balance = MchBalance(**balance)
        session.add(mch_balance)

        # 支持多种支付类型 万分率
        use_old_payment_type = False
        for payment_type in PAY_TYPES:
            payment_rate = getattr(
                self.form, 'payment_type' + str(payment_type)).data
            if payment_rate is not None:
                use_old_payment_type = True
                data = {
                    'mch_id': self.mch_id,
                    'payment_type': payment_type,
                    'payment_rate': payment_rate,
                    'activated_status': 1,
                    'create_at': datetime.datetime.now(),
                    'update_at': datetime.datetime.now(),
                    'dt_id': self.dt_id,
                    'settle_rate': payment_rate,
                }
                tmp_str = translate_payment_type.get(payment_type)
                if tmp_str:
                    uline_payment_id, uline_settle_id, trade_type,\
                        thirdparty_mch_id, uline_payment_code = tmp_str.split('|')
                    data['uline_payment_id'] = uline_payment_id
                    data['uline_settle_id'] = uline_settle_id
                    data['trade_type'] = trade_type
                    data['thirdparty_mch_id'] = thirdparty_mch_id
                    data['uline_payment_code'] = uline_payment_code
                    # 添加手续费和垫资费
                    if uline_payment_code.find('WX') != -1 and self.wx_draw_fee:
                        data['withdraw_fee'] = self.wx_draw_fee
                        if FEATURE_SWITCH.get('NEW_INLET'):
                            if self.wx_draw_rate:
                                data['withdraw_rate'] = self.wx_draw_rate
                            else:
                                withdraw_rate = self.get_dt_withdraw_rate(session, 'WX')
                                if withdraw_rate:
                                    data['withdraw_rate'] = withdraw_rate
                    if uline_payment_code.find('ALI') != -1 and self.ali_draw_fee:
                        data['withdraw_fee'] = self.ali_draw_fee
                        if FEATURE_SWITCH.get('NEW_INLET'):
                            if self.ali_draw_rate:
                                data['withdraw_rate'] = self.ali_draw_rate
                            else:
                                withdraw_rate = self.get_dt_withdraw_rate(session, 'ALI')
                                if withdraw_rate:
                                    data['withdraw_rate'] = withdraw_rate
                    # paymnet_type减去100
                    if FEATURE_SWITCH.get('NEW_INLET') and data.get('withdraw_rate') and data.get('payment_type') > 100:
                        data['payment_type'] -= 100
                        data['payment_rate'] -= data['withdraw_rate']
                        data['settle_rate'] -= data['withdraw_rate']
                        # 有手续费和垫资费，则为d0， uline_settle_id=2
                        data['uline_settle_id'] = 2

                mch_payment = MchPayment(**data)
                session.add(mch_payment)

        # 保存新的费率
        if not use_old_payment_type:
            for uline_payment_code in NEW_AVAILABLE_PAYMENTS.keys():
                payment_rate = getattr(self.form, uline_payment_code).data
                if payment_rate >= 0:
                    old_paymnet_type = new_payment_relations.get(uline_payment_code)
                    # 判断d0 or d1
                    if uline_payment_code.endswith('D0'):
                        uline_settle_id = 2
                        uline_payment_code = uline_payment_code[:-3]
                    else:
                        uline_settle_id = 1
                    uline_payment = UlinePayment.get_by(payment_code=uline_payment_code).first()
                    data = {
                        'mch_id': self.mch_id,
                        'payment_type': old_paymnet_type,
                        'settle_rate': payment_rate,
                        'payment_rate': payment_rate,
                        'activated_status': 1,
                        'create_at': datetime.datetime.now(),
                        'update_at': datetime.datetime.now(),
                        'dt_id': self.dt_id,
                        'uline_payment_code': uline_payment_code,
                        'uline_payment_id': uline_payment.id,
                        'trade_type': uline_payment.trade_type,
                        'uline_settle_id': uline_settle_id
                    }
                    # 添加手续费和垫资费
                    if uline_payment_code.find('WX') != -1 and self.wx_draw_fee:
                        data['withdraw_fee'] = self.wx_draw_fee
                        data['uline_settle_id'] = 2
                        if FEATURE_SWITCH.get('NEW_INLET'):
                            if self.wx_draw_rate:
                                data['withdraw_rate'] = self.wx_draw_rate
                            else:
                                withdraw_rate = self.get_dt_withdraw_rate(session, 'WX')
                                if withdraw_rate:
                                    data['withdraw_rate'] = withdraw_rate
                    if uline_payment_code.find('ALI') != -1 and self.ali_draw_fee:
                        data['withdraw_fee'] = self.ali_draw_fee
                        data['uline_settle_id'] = 2
                        if FEATURE_SWITCH.get('NEW_INLET'):
                            if self.ali_draw_rate:
                                data['withdraw_rate'] = self.ali_draw_rate
                            else:
                                withdraw_rate = self.get_dt_withdraw_rate(session, 'ALI')
                                if withdraw_rate:
                                    data['withdraw_rate'] = withdraw_rate
                    mch_payment = MchPayment(**data)
                    session.add(mch_payment)

    def get_dt_withdraw_rate(self, session, type):
        try:
            return session.query(DtPayment).filter(DtPayment.uline_payment_code.startswith(type),
                                                   DtPayment.dt_id == self.dt_id).first().withdraw_rate
        except Exception:
            return None

    def add_auth_inlet_info(self, session):

        data = {
            'mch_id': self.mch_id,
            'comment': u'提交审核',
            'auth_user': session.query(DtUser).filter_by(
                dt_id=self.dt_id).first().dt_name,
            'auth_status': 1,
            'create_at': datetime.datetime.now()
        }
        auth_info = AuthMchInfo(**data)
        session.add(auth_info)

    def add_d0_withdraw_fee(self, session):
        # 数据库只能存int
        wx_draw_fee = self.wx_draw_fee
        ali_draw_fee = self.ali_draw_fee
        data = {
            'role': self.mch_id,
            'role_type': 'mch',
            'wx': wx_draw_fee,
            'alipay': ali_draw_fee,
            'update_at': datetime.datetime.now(),
            'create_at': datetime.datetime.now()
        }
        withdraw_pay = D0WithdrawPay(**data)
        session.add(withdraw_pay)

    def check_dine_img(self):
        # 进件补充材料
        has_dine_annex_imgs = False
        for img_count in range(1, 6):
            img_name = 'wx_dine_annex_img' + str(img_count)
            result = self.save_img(img_name, 500, u'围餐补充材料')
            if not has_dine_annex_imgs:
                has_dine_annex_imgs = result
        return has_dine_annex_imgs

    def save_img(self, img_name, max_size, default_key_name=''):
        img_data = getattr(self.form, img_name).raw_data
        have_save_img = False
        if img_data:
            img_length = len(img_data[0].get('body'))
            if img_length > max_size * 1024:
                self.form.errors['img'] = [u'{}照片不得大于{}Kb'.format(default_key_name, max_size)]
                raise RESTfulHTTPError(content=self.form.errors)

            # 没有返回说明符合条件，保存图片
            setattr(self, img_name, self.save_idCard_img(self.request.files.get(img_name)))
            have_save_img = True
        else:
            # 说明图片为空，保存一个None
            setattr(self, img_name, None)
        return have_save_img

    def update_employee_profile(self, session):

        status = 2
        creator_id = 0
        create_at = update_at = datetime.datetime.now()
        user_id = session.query(func.max(Employee.id)).first()
        user_id = user_id[0] + 1 if user_id[0] else 10000000
        sys_type_id = session.query(SysType).filter(SysType.code == "mch").one()
        new_user = UserProfile(
            id=user_id,
            name=self.mch_name,
            city=self.city,
            phone1=self.mobile,
            email=self.email,
            sex=None,
            status=status,
            creator_id=creator_id,
            create_at=create_at,
            update_at=update_at
        )
        login_employee = Employee(
            id=user_id,
            sys_id=self.mch_id,
            login_passwd=self._password,
            login_name=str(self.mch_id) + ".mch",

            sys_type_id=sys_type_id.id,
            create_at=create_at,
            update_at=update_at,
            creator_id=creator_id,
            status=status,
            user_id=user_id

        )
        session.add(new_user)
        session.add(login_employee)
        session.commit()


        if self.cs_id is None:
            role_id = session.query(Role) \
                .filter(Role.sys_type_id == sys_type_id.id, Role.sp_type == 1).one()
            employee_role = EmployeeRolePermit(employee_id=user_id, role_id=role_id.id)
            session.add(employee_role)

        new_create_record = EmployeeUserLog(eutype=1,
                                            employee_id=user_id,
                                            comment="成功创建账号",
                                            operate_id=0,
                                            create_at=create_at)
        session.add(new_create_record)
        session.commit()
