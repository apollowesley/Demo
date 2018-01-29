#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from datetime import date

import re
# from uline.settings import cur_dir
from os import path
from wtforms import validators, fields, ValidationError, RadioField
from wtforms.validators import NumberRange, URL

import uline.handlers.app.distributor.utils.form as dist_form_utils
from uline.model.uline.base import uline_session
from uline.model.uline.info import DtPayment
from uline.model.uline.user import DtUser
from uline.public.baseDB import DbClient
from uline.public.constants import PAYMENT, AVAILABLE_PAYMENTS
from uline.utils.dayzero import form_verify
from uline.utils.form import File, BaseForm, BaseInletForm


def validate_mch_id(form, field):
    ret = db.selectSQL(
        "SELECT count(*) FROM mch_inlet_info WHERE dt_id=%s AND mch_id=%s",
        (form.dt_id, field.data)
    )

    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


def validate_chain_id(form, field):
    ret = db.selectSQL(
        "SELECT count(*) FROM dt_inlet_info WHERE parent_id=%s AND dt_id=%s",
        (form.dt_id, field.data)
    )

    if not ret[0]:
        raise ValidationError(u'该商户号不存在,请确认输入')


def validate_new_payment_rate(form, field):
    # eg: WX_OFFLINE_NATIVE or WX_OFFLINE_NATIVE_D0
    try:
        platform, channel, payment_type = re.split('_', field.name)
    except Exception:
        platform, channel, payment_type, settle = re.split('_', field.name)
        if settle != 'D0':
            payment_type = 'H5_DEBIT'
    if not platform and not channel and not payment_type:
        raise ValidationError(u'费率类型错误')

    payment_name = AVAILABLE_PAYMENTS.get(field.name)

    if not payment_name:
        raise ValidationError(u'无效支付类型-%s' % field.name)

    data = None
    try:
        data = float(field.data)
    except Exception:
        pass

    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'%s的费率小数不得超过1位' % payment_name)

    # 微信线下费率不得低于千2
    if platform == 'WX' and channel == 'OFFLINE' and isinstance(data, float) and data < 2:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)

    # 微信线上费率不得低于千6
    if platform == 'WX' and channel == 'ONLINE' and isinstance(data, float) and data < 6:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于6' % payment_name)

    # 微信0费率/微信围餐，只能为0
    if platform == 'WX' and channel in ['ZERO', 'DINE'] and isinstance(data, float) and data not in [0, 0.0]:
        raise ValidationError(u'%s的费率设置错误, 必须为0' % payment_name)

    # 支付宝线上费率不得低于千2
    if platform == 'ALI' and channel == 'OFFLINE' and isinstance(data, float) and data < 2:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)

    # 应产品经理需求，目前只要渠道商判断是否有添加这个支付类型
    dt_payment = uline_session.query(DtPayment).filter(DtPayment.dt_id == form.dt_id,
                                                       DtPayment.payment_type == int(payment_type)).first()

    if dt_payment is None:
        raise ValidationError(u'渠道商没有设置{}的费率'.format(payment_name))
    else:
        try:
            if dt_payment.payment_rate > field.data * 10:
                raise ValidationError(u'不能低于渠道商设置{}的费率'.format(payment_name))
            # elif dt_user.rate == 1 and float(field.data) > 0.0 and payment_type in [1, 2, 3]:
            #     raise ValidationError(
            #         u'0费率商户不能设置大于0的{}费率'.format(payment_name))
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_draw_rate(form, field):
    data = None
    try:
        data = float(field.data)
    except Exception:
        pass
    if isinstance(data, float):
        if data < 0.0:
            raise ValidationError(
                u'垫资费率设置错误, 需设置大于0')


def validate_payment_rate(form, field):
    payment_type = int(field.name[-1])
    payment_name = PAYMENT[str(payment_type)]

    if str(field.data)[::-1].find('.') > 1:
        raise ValidationError(u'{}的费率小数不得超过1位'.format(
            payment_name))
    if not 0 <= field.data < 10000:
        raise ValidationError(u'{}的费率为0~1000'.format(
            payment_name))  # 1000为迎合网页需求

    # 应产品经理需求，目前只要渠道商判断是否有添加这个支付类型
    dt_payment = uline_session.query(DtPayment).filter(DtPayment.dt_id == form.dt_id,
                                                       DtPayment.payment_type == int(payment_type)).first()

    if dt_payment is None:
        raise ValidationError(u'渠道商没有设置{}的费率'.format(payment_name))
    else:
        dt_user = DtUser.get_by(dt_id=form.dt_id).first()
        try:
            if dt_payment.payment_rate > field.data * 10:
                raise ValidationError(u'不能低于渠道商设置{}的费率'.format(payment_name))
            elif dt_user.rate == 1 and float(field.data) > 0.0 and payment_type in [1, 2, 3]:
                raise ValidationError(
                    u'0费率商户不能设置大于0的{}费率'.format(payment_name))
        except TypeError:
            raise ValidationError(u'费率必须为数字')


db = DbClient()

cur_dir = path.dirname(path.dirname(path.abspath(__file__)))


def validate_check_item1(form, field):
    if not field.data:
        raise ValidationError(u'微信－扫码支付的费率必须大于0')


def validate_check_item2(form, field):
    if not field.data:
        raise ValidationError(u'微信－刷卡支付的费率必须大于0')


def validate_check_item3(form, field):
    if not field.data:
        raise ValidationError(u'微信－公众账号支付的费率必须大于0')


def validate_check_item4(form, field):
    if not field.data:
        raise ValidationError(u'微信－APP支付的费率必须大于6')


def validate_check_item7(form, field):
    if not field.data:
        raise ValidationError(u'支付宝－扫码支付的费率必须大于0')


def validate_check_item8(form, field):
    if not field.data:
        raise ValidationError(u'支付宝－刷卡支付的费率必须大于0')


def validate_check_item9(form, field):
    if not field.data:
        raise ValidationError(u'支付宝－JS支付的费率必须大于0')


def validate_balance_way(form, field):
    if field.data not in ['T+1', 'D+0']:
        raise ValidationError(u'结算方式是T+1或者D+0')


def validate_balance_type(form, field):
    if field.data not in [u'企业', u'个人']:
        raise ValidationError(u'结算账号类型是企业或者个人')


def validate_bank_no(form, field):
    ret = db.selectSQL(
        "select 1 from balance_bank_info where bank_no=%s", (field.data,))
    if not ret:
        raise ValidationError(u'结算支行联行号错误')


def validate_industry_code(form, field):
    ret = db.selectSQL(
        "select 1 from industry_uline_info where industry_code=%s;",
        (field.data,)
    )
    if not ret:
        raise ValidationError(u'行业类别错误')


def validate_payment_type(form, field):
    if field.data not in ['微信－扫码支付', '微信－刷卡支付', '微信－公众账号支付']:
        raise ValidationError(u'支付类型错误')


def validate_mch_payment_rate1(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s",
        (form.dt_id, 1)
    )
    if not ret:
        raise ValidationError(u'渠道商没有设置微信－扫码支付的费率')
    else:
        rate = db.selectSQL(
            'select rate from dt_user where dt_id=%s;',
            (form.dt_id,)
        )
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置微信－扫码支付的费率')
            elif rate[0] == 1 and float(field.data) > 0.0:
                raise ValidationError(u'0费率商户微信－扫码支付的费率必须为0')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate2(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s",
        (form.dt_id, 2)
    )
    if not ret:
        raise ValidationError(u'渠道商没有设置微信－刷卡支付的费率')
    else:
        rate = db.selectSQL(
            'select rate from dt_user where dt_id=%s;',
            (form.dt_id,)
        )
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置微信－刷卡支付的费率')
            elif rate[0] == 1 and float(field.data) > 0.0:
                raise ValidationError(u'0费率商户微信-刷卡支付的费率必须为0')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate3(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s",
        (form.dt_id, 3)
    )
    if not ret:
        raise ValidationError(u'渠道商没有设置微信－公众账号支付的费率')
    else:
        rate = db.selectSQL(
            'select rate from dt_user where dt_id=%s;',
            (form.dt_id,)
        )
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置微信－公众账号支付的费率')
            elif rate[0] == 1 and float(field.data) > 0.0:
                raise ValidationError(u'0费率商户微信－公众账号支付的费率必须为0')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate4(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s", (form.dt_id, 4))
    if not ret:
        raise ValidationError(u'渠道商没有设置微信－APP支付的费率')
    else:
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置微信－APP支付的费率')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate5(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s", (form.dt_id, 5))
    if not ret:
        raise ValidationError(u'渠道商没有设置微信－H5支付的费率')
    else:
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置微信－H5支付的费率')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate7(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s",
        (form.dt_id, 7)
    )
    if not ret:
        raise ValidationError(u'渠道商没有设置支付宝－扫码支付的费率')
    else:
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置支付宝－扫码支付的费率')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate8(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s",
        (form.dt_id, 8)
    )
    if not ret:
        raise ValidationError(u'渠道商没有设置支付宝－刷卡支付的费率')
    else:
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置支付宝－刷卡支付的费率')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate9(form, field):
    ret = db.selectSQL(
        "select payment_rate from dt_payment where dt_id=%s and payment_type=%s",
        (form.dt_id, 9)
    )
    if not ret:
        raise ValidationError(u'渠道商没有设置支付宝－JS支付的费率')
    else:
        try:
            if ret[0] > float(field.data) * 10.0:
                raise ValidationError(u'不能低于渠道商设置支付宝－JS支付的费率')
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_mch_payment_rate21(form, field):
    data = None
    try:
        data = float(field.data)
    except Exception:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'京东－扫码支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'京东－扫码支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate22(form, field):
    data = None
    try:
        data = float(field.data)
    except Exception:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'京东－刷卡支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'京东－刷卡支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate23(form, field):
    data = None
    try:
        data = float(field.data)
    except Exception:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'京东－公众号支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'京东－公众号支付的费率设置错误, 需设置为大于等于2')


def validate_mch_payment_rate33(form, field):
    data = None
    try:
        data = float(field.data)
    except Exception:
        pass
    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'银联－JS支付的费率小数不得超过1位')
    if isinstance(data, float):
        if data < 2:
            raise ValidationError(u'银联－JS支付的费率设置错误, 需设置为大于等于2')


def validate_id_card_f_path(form, field):
    base_img_dir = path.normpath(
        path.join(cur_dir, '../../../static/uploads/tmp/mch/idcard/'))
    # base_img_dir = path.join(cur_dir, 'static/uploads/tmp/mch/idcard/')
    file_dir = path.join(base_img_dir, '{}'.format(
        form.dt_id), '{}'.format(form.uuid), '{}'.format(field.data))
    if not path.exists(file_dir):
        raise ValidationError(u'不存在身份证正面照片')


def validate_img_path(form, field):
    dine_img_dict = {
        'mch_desk_img': u'不存在收银台照片',
        'mch_front_img': u'不存在门店门口照片',
        'mch_inner_img': u'不存在门店内部环境照片',
        'annex_img1': u'不存在进件补充照片',
        'annex_img2': u'不存在进件补充照片',
        'annex_img3': u'不存在进件补充照片',
        'annex_img4': u'不存在进件补充照片',
        'annex_img5': u'不存在进件补充照片',
    }
    for i in range(1, 6):
        dine_img_dict['wx_dine_annex_img' + str(i)] = u'不存在围餐补充材料照片'
    base_img_dir = path.normpath(
        path.join(cur_dir, '../../../static/uploads/tmp/mch/idcard/'))
    # base_img_dir = path.join(cur_dir, 'static/uploads/tmp/mch/idcard/')
    file_dir = path.join(base_img_dir, '{}'.format(
        form.dt_id), '{}'.format(form.uuid), '{}'.format(field.data))
    if not path.exists(file_dir):
        raise ValidationError(dine_img_dict.get(field.name))


def validate_id_card_b_path(form, field):
    base_img_dir = path.normpath(
        path.join(cur_dir, '../../../static/uploads/tmp/mch/idcard/'))
    # base_img_dir = path.join(cur_dir, 'static/uploads/tmp/mch/idcard/')
    file_dir = path.join(base_img_dir, '{}'.format(
        form.dt_id), '{}'.format(form.uuid), '{}'.format(field.data))
    if not path.exists(file_dir):
        raise ValidationError(u'不存在身份证反面照片')


def validate_license_img_path(form, field):
    base_img_dir = path.normpath(
        path.join(cur_dir, '../../../static/uploads/tmp/mch/idcard/'))
    # base_img_dir = path.join(cur_dir, 'static/uploads/tmp/mch/idcard/')
    file_dir = path.join(base_img_dir, '{}'.format(
        form.dt_id), '{}'.format(form.uuid), '{}'.format(field.data))
    if not path.exists(file_dir):
        raise ValidationError(u'不存在营业执照照片')


def validate_wx_use_parent(form, field):
    """
    现在已经不支持大商户模式
    """
    if field.data != '1':
        raise ValidationError(u'不支持使用渠道appid')


def validate_license_period(form, field):
    if not (form.licenseEndDate.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')


def validate_license_end_date(form, field):
    if not (form.licensePeriod.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    today = date.today()
    if field.data and (field.data - today).days < 90:
        raise ValidationError(u'营业执照有效期不足3个月')


# 验证字段是否有空格


def is_has_space(form, field):
    if re.search(r' ', str(field.data)):
        raise ValidationError(str(field.data) + u' 包含空格, 请修改！')


# 验证客服电话字段
def validate_service_phone(form, field):
    if not (re.match('((^\d{5}$)|(^\d{7,8}$)|(^\d{10,12}$)|(^\d{2,4}-\d{1,'
                     '5}$)|(^\d{2,4}-\d{7,8}$)|(^\d{5,8}-\d{1,5})|(^\d{3,'
                     '4}-\d{3,8}-\d{1,4}$))', str(field.data))):
        raise ValidationError(str(field.data) + u'客服电话无效, 请修改！')


def validate_license_period_upload(form, field):
    if not (form.license_end_date.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    if str(field.data) not in (['1', '2']):
        raise ValidationError(u'仅可填写是或否')


def validate_license_end_date_upload(form, field):
    if not (form.license_period.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    else:
        today = date.today()
        if field.data and (field.data - today).days < 90:
            raise ValidationError(u'营业执照有效期不足3个月')


# def validate_chain_id(form, filed):
    # ret = db.selectSQL(
        # "select dt_name from dt_inlet_info where dt_id=%s and parent_id=%s",
        # (filed.data, form.dt_id)
    # )
    # if not ret:
        # raise ValidationError(u'渠道商没有该连锁商户')


# def validate_chain_id(form, field):
#     ret = db.selectSQL("SELECT count(*) FROM dt_inlet_info WHERE dt_id=%s and parent_id NOTNULL",
#                        (field.data,))
#     if not ret[0]:
#         raise ValidationError(u'该渠道商号不存在,请确认输入')

class ResendMchActiveEmail(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户ID不能为空'), validate_mch_id])


class UploadCsInletImage(BaseForm):
    img_file = fields.FileField('img_file', validators=[File])
    uuid = fields.StringField(
        validators=[validators.Length(min=20, message=u'无效的提交参数')])


class UploadCSInletExcel(BaseForm):
    xls_file = fields.FileField('xls_file', validators=[File])


class UploadCsInletInfo(BaseForm):
    uuid = fields.StringField(
        validators=[validators.Length(min=20, message=u'无效的提交参数')])


class CSBatchInletInfo(BaseInletForm):
    mch_name = fields.StringField(
        validators=[validators.DataRequired(message=u'商户名称不能为空'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=64, message=u'无效商户简称'), is_has_space])
    industry_code = fields.StringField(
        validators=[
            validators.Length(min=15, max=15, message=u'无效行业类别'),
            validate_industry_code,
            is_has_space
        ]
    )
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份')])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市')])
    # 新增areaname
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效区域')])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址')])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(validators=[validators.Email(message=u'无效邮箱')])
    balance_type = fields.StringField(
        validators=[
            validators.Length(min=2, max=30, message=u'无效结算账号类型'),
            validate_balance_type
        ]
    )
    balance_name = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算户名'), is_has_space])
    bank_name_com = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算银行'), is_has_space])
    bank_name = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算支行'), is_has_space])
    bank_no = fields.StringField(validators=[validators.Length(
        min=2, max=30, message=u'无效结算支行联行号'), validate_bank_no, is_has_space])
    balance_account = fields.StringField(
        validators=[validators.Length(min=2, max=30, message=u'无效结算账号'), is_has_space])
    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效身份证正面照片'), validate_id_card_f_path])
    id_card_img_b = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效身份证反面照片'), validate_id_card_b_path])
    # D1
    checkItem1 = fields.DecimalField()
    checkItem2 = fields.DecimalField()
    checkItem3 = fields.DecimalField()
    checkItem4 = fields.DecimalField()
    checkItem7 = fields.DecimalField()
    checkItem8 = fields.DecimalField()
    checkItem9 = fields.DecimalField()

    # D0
    checkItem101 = fields.DecimalField()
    checkItem102 = fields.DecimalField()
    checkItem103 = fields.DecimalField()
    checkItem104 = fields.DecimalField()
    checkItem107 = fields.DecimalField()
    checkItem108 = fields.DecimalField()
    checkItem109 = fields.DecimalField()

    wx = fields.FloatField()
    alipay = fields.FloatField()

    wx_use_parent = fields.StringField(
        'wx_use_parent',
        default='1'
    )

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号'),
            is_has_space
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date_upload
        ]
    )
    license_period = fields.StringField(
        'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period_upload
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )
    dt_sub_id = fields.IntegerField(validators=[validators.Optional(),
                                                dist_form_utils.validate_dt_sub_id_enable])
    cs_id = fields.StringField()


class AddMerchantlnlet(BaseForm):
    mch_name = fields.StringField(
        validators=[validators.Length(min=2, max=40, message=u'无效商户名'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=18, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validate_industry_code, is_has_space])
    # jobType = fields.StringField(
    # validators=[validators.Length(min=15, max=15, message=u'无效行业类别'),
    # is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效区域'), is_has_space])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址'), is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])
    activate_email_tag = fields.IntegerField(validators=[validators.AnyOf([1, 2])])
    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    balance_account = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效银行名称'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=9, max=23, message=u'无效结算账户'), is_has_space])
    bankName = fields.StringField()
    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])

    id_card_img_f = fields.FileField('imgCardFront', validators=[File])
    id_card_img_b = fields.FileField('imgCardBack', validators=[File])

    # 银联新字段
    # 负责人
    head_name = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=2, max=20, message=u'无效负责人姓名'),
        is_has_space])
    # 负责人电话
    head_mobile = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=5, max=15, message=u'负责人电话'),
        validate_service_phone, is_has_space])
    # 负责人类型
    head_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(["LEGAL_PERSON", "CONTROLLER", "AGENT", "OTHER"])
        ]
    )
    # 手持身份证照片
    img_with_id_card = fields.FileField('img_with_id_card', validators=[File])

    wx_use_parent = RadioField(
        'wx_use_parent',
        [validators.Required()],
        choices=[('1', '不使用'), ('2', '使用')], default='1'
    )
    payment_type1 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type2 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type3 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type4 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type5 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type7 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type8 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type9 = fields.DecimalField(
        validators=[validators.Optional()])

    payment_type21 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－扫码支付的费率为2~1000'),
            validate_mch_payment_rate21
        ],
        places=1)
    payment_type22 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－刷卡支付的费率为2~1000'),
            validate_mch_payment_rate22
        ],
        places=1)
    payment_type23 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－公众账号支付的费率为2~1000'),
            validate_mch_payment_rate23
        ],
        places=1)

    # 银联
    payment_type33 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'银联－JS支付的费率为2~1000'),
            validate_mch_payment_rate33
        ],
        places=1)

    # d0费率，统一在API进行验证
    payment_type101 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type102 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type103 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type104 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type105 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type107 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type108 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type109 = fields.DecimalField(
        validators=[validators.Optional()])

    # 微信线下
    WX_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    WX_ONLINE_APP = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    UNIONPAY_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 支付宝0费率
    ALI_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    ALI_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    ALI_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # D0 临时方案
    # 微信线下
    WX_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    WX_ONLINE_APP_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 京东线下
    JD_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    JD_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    JD_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    JD_ONLINE_H5 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付的费率为2~1000'),
            validate_new_payment_rate
        ],
        places=1)

    JD_ONLINE_H5_DEBIT = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付(借记卡)的费率为4~1000'),
            validate_new_payment_rate
        ],
        places=1)

    # D0提现手续费
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误'),
            form_verify.range_fee
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误'),
            form_verify.range_fee
        ]
    )
    # D0提现手续费
    wx_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误')
        ]
    )

    ali_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误')
        ]
    )

    # D0提现垫资费
    wx_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    ali_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    # 营业执照类型
    license_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(['NATIONAL_LEGAL', 'NATIONAL_LEGAL_MERGE', 'INST_RGST_CTF'])
        ]
    )

    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    license_period = fields.StringField(
        # 'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.FileField(
        'licenseImg',
        validators=[File]
    )
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])

    cs_id = fields.IntegerField(validators=[
        validators.Optional()
    ])

    use_dine = fields.StringField(validators=[validators.optional()])

    # 商户收银台照片
    mch_desk_img = fields.FileField(validators=[validators.optional(), File])
    # 商户门口照片
    mch_front_img = fields.FileField(validators=[validators.optional(), File])
    # 商户内部环境照片
    mch_inner_img = fields.FileField(validators=[validators.optional(), File])

    # 进件补充材料图片
    annex_img1 = fields.FileField(validators=[validators.optional(), File])
    annex_img2 = fields.FileField(validators=[validators.optional(), File])
    annex_img3 = fields.FileField(validators=[validators.optional(), File])
    annex_img4 = fields.FileField(validators=[validators.optional(), File])
    annex_img5 = fields.FileField(validators=[validators.optional(), File])

    wx_dine_annex_img1 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img2 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img3 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img4 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img5 = fields.FileField(validators=[validators.optional(), File])

    # 用于前端判断是否勾选
    # 平台
    WX = fields.StringField(default='')
    ALI = fields.StringField(default='')
    JD = fields.StringField(default='')

    # 微信通道
    WX_OFFLINE = fields.StringField(default='')
    WX_ONLINE = fields.StringField(default='')
    WX_DINE = fields.StringField(default='')
    WX_ZERO = fields.StringField(default='')

    # D0
    WX_D0 = fields.StringField(default='')
    ALI_D0 = fields.StringField(default='')

    # D1
    WX_D1 = fields.StringField(default='')
    ALI_D1 = fields.StringField(default='')

    # 支付宝通道
    ALI_ZERO = fields.StringField(default='')
    ALI_OFFLINE = fields.StringField(default='')

    # 用于前端判断是否显示
    # 平台
    HAS_WX = fields.StringField(default='')
    HAS_ALI = fields.StringField(default='')

    # 微信通道
    HAS_WX_OFFLINE = fields.StringField(default='')
    HAS_WX_ONLINE = fields.StringField(default='')
    HAS_WX_DINE = fields.StringField(default='')
    HAS_WX_ZERO = fields.StringField(default='')

    # D0
    HAS_WX_D0 = fields.StringField(default='')
    HAS_ALI_D0 = fields.StringField(default='')

    # D1
    HAS_WX_D1 = fields.StringField(default='')
    HAS_ALI_D1 = fields.StringField(default='')

    # 支付宝通道
    HAS_ALI_ZERO = fields.StringField(default='')
    HAS_ALI_OFFLINE = fields.StringField(default='')


class MerchantSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    mch_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3])])
    total_num = fields.IntegerField()
    mch_id = fields.StringField()
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])
    cs_id = fields.StringField()


class CsSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    short_name = fields.StringField()
    cs_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3, 4])])
    total_num = fields.IntegerField()
    cs_id = fields.StringField()
    mch_id = fields.StringField()


class BankInfo(BaseForm):
    # 列出渠道商的商户
    q = fields.StringField(
        validators=[validators.DataRequired(message=u'查询字符不能为空')])
    page = fields.IntegerField(
        validators=[validators.Optional(),
                    validators.NumberRange(min=1, max=1000)])


class ResendChainActiveEmail(BaseForm):
    # 获取商户信息ajax接口
    chain_id = fields.IntegerField(
        validators=[validators.DataRequired(message=u'商户ID不能为空'), validate_chain_id])


class GetMerchanInfo(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id
        ]
    )


class GetMerchanPayCallbackUrl(BaseForm):
    # 获取商户支付回调信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id
        ]
    )
    pay_notify_url = fields.StringField(
        validators=[
            URL(message=u"URL格式不正确"),
        ]
    )


class ModifyMerchantlnlet(BaseForm):
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id,
            is_has_space
        ]
    )
    mch_name = fields.StringField(
        validators=[validators.Length(min=2, max=40, message=u'无效商户名'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=18, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validators.Length(min=15, max=15, message=u'无效行业类别'), is_has_space])
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效区域'), is_has_space])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址'), is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])
    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效支联代码'), is_has_space])
    bankName = fields.StringField()
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=23, message=u'无效结算账户'), is_has_space])
    id_card_no = fields.StringField(validators=[validators.Length(
        min=1, max=20, message=u'无效身份证号码'), is_has_space])

    imgCardFrontOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    imgCardBackOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])

    id_card_img_f = fields.FileField('imgCardFront')
    id_card_img_b = fields.FileField('imgCardBack')

    # 银联新字段
    # 负责人
    head_name = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=2, max=20, message=u'无效负责人姓名'),
        is_has_space])
    # 负责人电话
    head_mobile = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=5, max=15, message=u'负责人电话'),
        validate_service_phone,
        is_has_space])
    # 负责人类型
    head_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(["LEGAL_PERSON", "CONTROLLER", "AGENT", "OTHER"])
        ]
    )
    # 手持身份证照片
    img_with_id_card = fields.FileField('img_with_id_card', validators=[File])

    payment_type1 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'微信－扫码支付的费率为0~1000'),
            validate_mch_payment_rate1
        ],
        places=1
    )
    payment_type2 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'微信－线下小额支付的费率为0~1000'),
                    validate_mch_payment_rate2], places=1)
    payment_type3 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'微信－公众账号支付的费率为0~1000'),
                    validate_mch_payment_rate3], places=1)
    payment_type4 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'微信－APP支付的费率为0~1000'),
                    validate_mch_payment_rate4], places=1)
    payment_type5 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'微信－H5支付的费率为0~1000'),
                    validate_mch_payment_rate5], places=1)
    payment_type7 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'支付宝－扫码支付的费率为0~1000'),
                    validate_mch_payment_rate7], places=1)
    payment_type8 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'支付宝－刷卡支付的费率为0~1000'),
                    validate_mch_payment_rate8], places=1)
    payment_type9 = fields.DecimalField(
        validators=[validators.Optional(), NumberRange(0, 1000, message=u'支付宝－JS支付的费率为0~1000'),
                    validate_mch_payment_rate9], places=1)

    payment_type21 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－扫码支付的费率为2~1000'),
            validate_mch_payment_rate21
        ],
        places=1)
    payment_type22 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－刷卡支付的费率为2~1000'),
            validate_mch_payment_rate22
        ],
        places=1)
    payment_type23 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'京东－公众账号支付的费率为2~1000'),
            validate_mch_payment_rate23
        ],
        places=1)

    # 银联
    payment_type33 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(2, 1000, message=u'银联－JS支付的费率为2~1000'),
            validate_mch_payment_rate33
        ],
        places=1)

    # d0费率，统一在API进行验证
    payment_type101 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type102 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type103 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type104 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type105 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type107 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type108 = fields.DecimalField(
        validators=[validators.Optional()])
    payment_type109 = fields.DecimalField(
        validators=[validators.Optional()])

    # 微信线下
    WX_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    WX_ONLINE_APP = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 支付宝0费率
    ALI_ZERO_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    ALI_ZERO_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    ALI_ZERO_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    UNIONPAY_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'银联－线下-公众号支付的费率为0~1000'),
            validate_payment_rate
        ],
        places=1)

    # D0 临时方案
    # 微信线下
    WX_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信线上
    WX_ONLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    WX_ONLINE_APP_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ONLINE_MWEB_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信围餐
    WX_DINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_DINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 微信0费率
    WX_ZERO_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    WX_ZERO_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 支付宝线下
    ALI_OFFLINE_NATIVE_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    ALI_OFFLINE_MICROPAY_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    ALI_OFFLINE_JSAPI_D0 = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # 京东线下
    JD_OFFLINE_NATIVE = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)
    JD_OFFLINE_MICROPAY = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    JD_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    JD_ONLINE_H5 = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付的费率为2~1000'),
            validate_new_payment_rate
        ],
        places=1)

    JD_ONLINE_H5_DEBIT = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000, message=u'京东－线上-h5支付(借记卡)的费率为4~1000'),
            validate_new_payment_rate
        ],
        places=1)

    # D0提现手续费
    # wx = fields.DecimalField(
    #     validators=[
    #         validators.Optional(),
    #         NumberRange(0, 1000000, message=u'D0-微信手续费设置错误'),
    #         form_verify.range_fee
    #     ]
    # )
    #
    # alipay = fields.DecimalField(
    #     validators=[
    #         validators.Optional(),
    #         NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误'),
    #         form_verify.range_fee
    #     ]
    # )
    # D0提现手续费
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误'),
            form_verify.range_fee
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误'),
            form_verify.range_fee
        ]
    )
    # D0提现手续费
    wx_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误')
        ]
    )

    ali_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误')
        ]
    )

    # D0提现垫资费
    wx_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    ali_draw_rate = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_draw_rate
        ]
    )

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号'),
            is_has_space
        ]
    )
    # 营业执照类型
    license_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(['NATIONAL_LEGAL', 'NATIONAL_LEGAL_MERGE', 'INST_RGST_CTF'])
        ]
    )

    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    license_period = fields.StringField(
        'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    licenseImgOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )
    img_with_id_cardOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )
    license_img = fields.FileField(
        'licenseImg',
        # validators=[File]
    )
    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])

    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()

    cs_id = fields.StringField()
    use_dine = fields.StringField(validators=[validators.optional()])

    # 商户收银台照片
    mch_desk_img = fields.FileField(validators=[validators.optional(), File])
    mch_desk_img_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    # 商户门口照片
    mch_front_img = fields.FileField(validators=[validators.optional(), File])
    mch_front_img_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    # 商户内部环境照片
    mch_inner_img = fields.FileField(validators=[validators.optional(), File])
    mch_inner_img_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])

    # 进件补充材料图片
    annex_img1 = fields.FileField(validators=[validators.optional()])
    annex_img2 = fields.FileField(validators=[validators.optional()])
    annex_img3 = fields.FileField(validators=[validators.optional()])
    annex_img4 = fields.FileField(validators=[validators.optional()])
    annex_img5 = fields.FileField(validators=[validators.optional()])
    annex_img1_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    annex_img2_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    annex_img3_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    annex_img4_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    annex_img5_old = fields.StringField(validators=[validators.Length(min=4, max=255, message=u'无效文件名')])

    # 删除哪些进件补充材料的图片
    # 字符串形式，用数字和-代表需要删除哪些图片，如：1  1-3  1-3-5
    del_annex = fields.StringField(validators=[validators.optional()])

    wx_dine_annex_img1 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img2 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img3 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img4 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img5 = fields.FileField(validators=[validators.optional(), File])

    wx_dine_annex_img1_old = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    wx_dine_annex_img2_old = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    wx_dine_annex_img3_old = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    wx_dine_annex_img4_old = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    wx_dine_annex_img5_old = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])

    del_wx_dine_annex = fields.StringField(validators=[validators.optional()])

    # 用于前端判断是否勾选
    # 平台
    WX = fields.StringField(default='')
    ALI = fields.StringField(default='')
    JD = fields.StringField(default='')

    # 微信通道
    WX_OFFLINE = fields.StringField(default='')
    WX_ONLINE = fields.StringField(default='')
    WX_DINE = fields.StringField(default='')
    WX_ZERO = fields.StringField(default='')

    # D0
    WX_D0 = fields.StringField(default='')
    ALI_D0 = fields.StringField(default='')

    # D1
    WX_D1 = fields.StringField(default='')
    ALI_D1 = fields.StringField(default='')

    # 支付宝通道
    ALI_ZERO = fields.StringField(default='')
    ALI_OFFLINE = fields.StringField(default='')

    # 用于前端判断是否显示
    # 平台
    HAS_WX = fields.StringField(default='')
    HAS_ALI = fields.StringField(default='')

    # 微信通道
    HAS_WX_OFFLINE = fields.StringField(default='')
    HAS_WX_ONLINE = fields.StringField(default='')
    HAS_WX_DINE = fields.StringField(default='')
    HAS_WX_ZERO = fields.StringField(default='')

    # D0
    HAS_WX_D0 = fields.StringField(default='')
    HAS_ALI_D0 = fields.StringField(default='')

    # D1
    HAS_WX_D1 = fields.StringField(default='')
    HAS_ALI_D1 = fields.StringField(default='')

    # 支付宝通道
    HAS_ALI_ZERO = fields.StringField(default='')
    HAS_ALI_OFFLINE = fields.StringField(default='')


class UploadMerchantInletExcel(BaseForm):
    xls_file = fields.FileField('xls_file', validators=[File])


class UploadMerchantInletImage(BaseForm):
    img_file = fields.FileField('img_file', validators=[File])
    uuid = fields.StringField(
        validators=[validators.Length(min=20, message=u'无效的提交参数')])


class UploadMerchantInletInfo(BaseForm):
    uuid = fields.StringField(
        validators=[validators.Length(min=20, message=u'无效的提交参数')])


class MerchantBatchInletInfo(BaseInletForm):
    mch_name = fields.StringField(
        validators=[validators.DataRequired(message=u'商户名称不能为空'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=54, message=u'无效商户简称'), is_has_space])
    industry_code = fields.StringField(
        validators=[
            validators.Length(min=15, max=15, message=u'无效行业类别'),
            validate_industry_code,
            is_has_space
        ]
    )
    province = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效省份')])
    city = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效城市')])
    address = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址')])
    # 新加了区域名称
    district = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效地址')])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])
    contact = fields.StringField(
        validators=[validators.Length(min=2, max=20, message=u'无效联系人'), is_has_space])
    mobile = fields.StringField(
        validators=[validators.Length(min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(validators=[validators.Email(message=u'无效邮箱')])
    balance_type = fields.StringField(
        validators=[
            validators.Length(min=2, max=30, message=u'无效结算账号类型'),
            validate_balance_type
        ]
    )
    balance_name = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算户名'), is_has_space])
    bank_name_com = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算银行'), is_has_space])
    bank_name = fields.StringField(
        validators=[validators.Length(min=2, max=255, message=u'无效结算支行'), is_has_space])
    bank_no = fields.StringField(validators=[validators.Length(
        min=2, max=30, message=u'无效结算支行联行号'), validate_bank_no, is_has_space])
    balance_account = fields.StringField(
        validators=[validators.Length(min=2, max=30, message=u'无效结算账号'), is_has_space])
    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效身份证正面照片'), validate_id_card_f_path])
    id_card_img_b = fields.StringField(validators=[validators.Length(
        min=2, max=64, message=u'无效身份证反面照片'), validate_id_card_b_path])

    payment_type1 = fields.StringField()
    payment_type2 = fields.StringField()
    payment_type3 = fields.StringField()
    payment_type4 = fields.StringField()
    payment_type7 = fields.StringField()
    payment_type8 = fields.StringField()
    payment_type9 = fields.StringField()

    wx_pay = fields.StringField()
    ali_pay = fields.StringField()
    d0_wx_pay = fields.StringField()
    d0_ali_pay = fields.StringField()
    wx = fields.StringField()
    alipay = fields.StringField()

    wx_use_parent = fields.StringField(
        'wx_use_parent',
        default='1'
    )

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号'),
            is_has_space
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
    license_end_date = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date_upload
        ]
    )
    license_period = fields.StringField(
        'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period_upload
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.StringField(
        validators=[validators.Length(min=5, max=255, message=u'无效文件名'),
                    validate_license_img_path
                    ]
    )

    dt_sub_id = fields.IntegerField(validators=[validators.Optional(),
                                                dist_form_utils.validate_dt_sub_id_enable])

    use_dine = fields.StringField(
        'use_dine',
        validators=[validators.Optional()]
    )

    # 商户收银台照片
    mch_desk_img = fields.StringField(validators=[validators.optional(), validators.Length(
        min=5, max=64, message=u'收银台照片必填'), validate_img_path])
    # 商户门口照片
    mch_front_img = fields.StringField(validators=[validators.optional(), validators.Length(
        min=5, max=64, message=u'门店门口照片必填'), validate_img_path])
    # 商户内部环境照片
    mch_inner_img = fields.StringField(validators=[validators.optional(), validators.Length(
        min=5, max=64, message=u'门店内部环境照片必填'), validate_img_path])

    # 进件补充材料图片
    annex_img1 = fields.StringField(validators=[validators.optional(), validate_img_path])
    annex_img2 = fields.StringField(validators=[validators.optional(), validate_img_path])
    annex_img3 = fields.StringField(validators=[validators.optional(), validate_img_path])
    annex_img4 = fields.StringField(validators=[validators.optional(), validate_img_path])
    annex_img5 = fields.StringField(validators=[validators.optional(), validate_img_path])

    wx_dine_annex_img1 = fields.StringField(validators=[validators.optional(), validate_img_path])
    wx_dine_annex_img2 = fields.StringField(validators=[validators.optional(), validate_img_path])
    wx_dine_annex_img3 = fields.StringField(validators=[validators.optional(), validate_img_path])
    wx_dine_annex_img4 = fields.StringField(validators=[validators.optional(), validate_img_path])
    wx_dine_annex_img5 = fields.StringField(validators=[validators.optional(), validate_img_path])


class GetMerchanWxConfig(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id
        ]
    )

    refresh = fields.IntegerField(validators=[validators.Optional()], default=1)


class SetMerchanWxConfig(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_mch_id
        ]
    )

    config_key = fields.StringField(
        validators.AnyOf(['subscribe_appid', 'sub_appid', 'jsapi_path'])
    )

    config_value = fields.StringField(
        validators.DataRequired(message=u'需要填写配置参数的值')
    )

    config_type = fields.IntegerField(
        'config_type', default='1'
    )


class AddChainGeneralForm(BaseForm):
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])
    activate_email_tag = fields.IntegerField(validators=[validators.AnyOf([1, 2])])

    chain_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=18, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validate_industry_code, is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])

    chain_name = fields.StringField(
        validators=[validators.Length(min=2, max=40, message=u'无效商户名'), is_has_space])
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(
        validators=[validators.Length(min=2, max=32, message=u'无效区域'), is_has_space])

    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])

    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.FileField('imgCardFront', validators=[File])
    id_card_img_b = fields.FileField('imgCardBack', validators=[File])

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )
    # 营业执照类型
    license_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(['NATIONAL_LEGAL', 'NATIONAL_LEGAL_MERGE', 'INST_RGST_CTF'])
        ]
    )
    license_start_date = fields.DateField(validators=[validators.Required()])
    licenseEndDate = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    licensePeriod = fields.StringField(
        # 'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.FileField(
        'licenseImg',
        validators=[File]
    )

    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效支联代码'), is_has_space])
    bankName = fields.StringField()
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=23, message=u'无效结算账户'), is_has_space])

    payment_type1 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    payment_type2 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    payment_type3 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    payment_type4 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    payment_type7 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    payment_type8 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    payment_type9 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])

    payment_type101 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    payment_type102 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    payment_type103 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    payment_type104 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    payment_type107 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    payment_type108 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    payment_type109 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])

    # D0提现手续费
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误'),
            form_verify.range_fee
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误'),
            form_verify.range_fee
        ]
    )

    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])

    # 负责人
    head_name = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=2, max=20, message=u'无效负责人姓名'),
        is_has_space])
    # 负责人电话
    head_mobile = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=5, max=15, message=u'负责人电话'),
        validate_service_phone, is_has_space])
    # 负责人类型
    head_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(["LEGAL_PERSON", "CONTROLLER", "AGENT", "OTHER"])
        ]
    )


class ChainSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0, 1, 2])], default=0)
    dt_name = fields.StringField()
    auth_status = fields.IntegerField(
        validators=[validators.Optional(), validators.AnyOf([0, 1, 2, 3, 4])], default=0)
    total_num = fields.IntegerField()
    dt_id = fields.StringField()


class CSSearch(BaseForm):
    # 列出渠道商的商户
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    activated_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2])])
    auth_status = fields.IntegerField(
        validators=[validators.AnyOf([0, 1, 2, 3, 4])])
    total_num = fields.IntegerField()

    cs_id = fields.StringField()
    cs_name = fields.StringField()
    mch_id = fields.StringField()
    short_name = fields.StringField()


class ChainInfoForm(BaseForm):
    # 获取商户信息ajax接口
    chain_id = fields.StringField(
        validators=[validators.DataRequired(message=u'查询字符不能为空'), validate_chain_id])


class ModifyChainlnletForm(BaseForm):
    chain_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_chain_id,
            is_has_space
        ]
    )

    # 连锁商户名称和行业类别不可变
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])

    chain_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=18, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validators.optional(), validate_industry_code, is_has_space])
    area = fields.StringField()
    cmbProvince = fields.StringField()
    cmbCity = fields.StringField()
    cmbArea = fields.StringField()
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), validate_service_phone, is_has_space])

    chain_name = fields.StringField(
        validators=[validators.optional(), validators.Length(min=2, max=40, message=u'无效商户名'), is_has_space])
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效城市'), is_has_space])
    district = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效区域'), is_has_space])
    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])

    id_card_no = fields.StringField(
        validators=[validators.Length(min=1, max=20, message=u'无效身份证号码'), is_has_space])
    id_card_img_f = fields.FileField('imgCardFront')
    id_card_img_b = fields.FileField('imgCardBack')

    license_num = fields.StringField(
        validators=[
            validators.required(),
            validators.Length(min=1, max=32, message=u'无效营业执照注册号')
        ]
    )

    # 营业执照类型
    license_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(['NATIONAL_LEGAL', 'NATIONAL_LEGAL_MERGE', 'INST_RGST_CTF'])
        ]
    )

    license_start_date = fields.DateField(validators=[validators.Required()])
    licenseEndDate = fields.DateField(
        validators=[
            validators.Optional(),
            validate_license_end_date
        ]
    )
    licensePeriod = fields.StringField(
        # 'licensePeriod',
        validators=[
            # validators.Optional(),
            validate_license_period
        ]
    )
    license_scope = fields.TextAreaField(
        validators=[
            validators.Length(max=500, message=u'营业范围内容太长')
        ]
    )
    license_img = fields.FileField('licenseImg')

    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型'), is_has_space])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(
        validators=[validators.Length(min=12, max=13, message=u'无效支联代码'), is_has_space])
    bankName = fields.StringField()
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=23, message=u'无效结算账户'), is_has_space])

    checkItem1 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    checkItem2 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    checkItem3 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    checkItem4 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    checkItem7 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    checkItem8 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])
    checkItem9 = fields.DecimalField(
        validators=[validators.Optional(), validate_payment_rate])

    checkItem101 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    checkItem102 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    checkItem103 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    checkItem104 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    checkItem107 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    checkItem108 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])
    checkItem109 = fields.DecimalField(
        validators=[validators.Optional(), form_verify.validate_payment_rate])

    # D0提现手续费
    wx = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-微信手续费设置错误'),
            form_verify.range_fee
        ]
    )

    alipay = fields.DecimalField(
        validators=[
            validators.Optional(),
            NumberRange(0, 1000000, message=u'D0-支付宝手续费设置错误'),
            form_verify.range_fee
        ]
    )

    dt_sub_id = fields.IntegerField(validators=[
        validators.Optional(), dist_form_utils.validate_dt_sub_id_exists,
    ])

    imgCardFrontOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    imgCardBackOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')])
    licenseImgOld = fields.StringField(
        validators=[validators.Length(min=4, max=255, message=u'无效文件名')]
    )

    # 负责人
    head_name = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=2, max=20, message=u'无效负责人姓名'),
        is_has_space])
    # 负责人电话
    head_mobile = fields.StringField(validators=[
        validators.Optional(),
        validators.Length(min=5, max=15, message=u'负责人电话'),
        validate_service_phone, is_has_space])

    # 负责人类型
    head_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(["LEGAL_PERSON", "CONTROLLER", "AGENT", "OTHER"])
        ]
    )


class GetChainWxConfig(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_chain_id
        ]
    )

    refresh = fields.IntegerField(validators=[validators.Optional()], default=1)


class SetChainWxConfig(BaseForm):
    # 获取商户信息ajax接口
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
            validate_chain_id
        ]
    )

    config_key = fields.StringField(
        validators.AnyOf(['subscribe_appid', 'sub_appid', 'jsapi_path'])
    )

    config_value = fields.StringField(
        validators.DataRequired(message=u'需要填写配置参数的值')
    )

    config_type = fields.IntegerField(
        'config_type', default='1'
    )
