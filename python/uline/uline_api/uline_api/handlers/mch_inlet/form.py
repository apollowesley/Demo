# -*- coding: utf-8 -*-
from __future__ import division
import re
from wtforms import ValidationError
from wtforms import validators, fields, RadioField
from uline_api.public.constants import NEW_AVAILABLE_PAYMENTS
from uline_api.util.form import BaseForm, File
from uline_api.model.uline.info import (
    DtPayment, BalanceBankInfo,
    UlineIndustryInfo, D0WithdrawPay, DtInletInfo
)
from uline_api.model.uline.user import DtUser
from uline_api.model.uline.user import DtSubUser
from datetime import date
from uline_api.model.uline.base import uline_session
from uline_api.setting import AVAILABLE_PAYMENTS, FEATURE_SWITCH


def validate_new_payment_rate(form, field):
    # eg: WX_OFFLINE_NATIVE or WX_OFFLINE_NATIVE_D0
    try:
        platform, channel, payment_type = re.split('_', field.name)
        uline_settle_id = 1
        uline_payment_code = field.name
    except:
        platform, channel, payment_type, settle = re.split('_', field.name)
        if field.name.endswith('_D0'):
            uline_settle_id = 2
            uline_payment_code = field.name[:-3]
        else:
            uline_settle_id = 1
            uline_payment_code = field.name

    if not platform and not channel and not payment_type:
        raise ValidationError(u'费率类型错误')

    payment_name = NEW_AVAILABLE_PAYMENTS.get(field.name)

    if not payment_name:
        raise ValidationError(u'无效支付类型-%s' % field.name)

    data = None
    try:
        data = float(field.data)
    except:
        pass

    if str(data)[::-1].find('.') > 1:
        raise ValidationError(u'%s的费率小数不得超过1位' % payment_name)

    # 线下费率不得低于千2
    if channel == 'OFFLINE' and isinstance(data, float) and data < 20:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)

    # 微信线上费率不得低于千6
    if platform == 'WX' and channel == 'ONLINE' and isinstance(data, float) and data < 60:
        raise ValidationError(u'%s的费率设置错误, 需设置为大于等于6' % payment_name)

    # 微信0费率/微信围餐，只能为0
    if platform == 'WX' and channel in ['ZERO', 'DINE'] and isinstance(data, float) and data not in [0, 0.0]:
        raise ValidationError(u'%s的费率设置错误, 必须为0' % payment_name)

    # 支付宝线上费率不得低于千2
    # if platform == 'ALI' and channel == 'OFFLINE' and isinstance(data, float) and data < 2:
    #     raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)
    #
    # # 京东线上费率不得低于千2
    # if platform == 'JD' and channel == 'OFFLINE' and isinstance(data, float) and data < 2:
    #     raise ValidationError(u'%s的费率设置错误, 需设置为大于等于2' % payment_name)

    # 应产品经理需求，目前只要渠道商判断是否有添加这个支付类型
    dt_payment = uline_session.query(DtPayment).filter(DtPayment.dt_id == form.dt_id,
                                                       DtPayment.uline_payment_code == uline_payment_code,
                                                       uline_settle_id == uline_settle_id).first()

    if dt_payment is None:
        raise ValidationError(u'渠道商没有设置{}的费率'.format(payment_name))
    else:
        dt_user = DtUser.get_by(dt_id=form.dt_id).first()
        try:
            if dt_payment.payment_rate > field.data:
                raise ValidationError(u'不能低于渠道商设置{}的费率'.format(payment_name))
            # elif dt_user.rate == 1 and float(field.data) > 0.0 and payment_type in [1, 2, 3]:
            #     raise ValidationError(
            #         u'0费率商户不能设置大于0的{}费率'.format(payment_name))
        except TypeError:
            raise ValidationError(u'费率必须为数字')


def validate_wx_use_parent(form, field):
    u = DtUser.get_by(dt_id=form.dt_id).first()
    if not u:
        raise ValidationError(u'渠道商未找到')
    if field.data in [2, '2'] and u.wx_sub_mch_id is None:
        raise ValidationError(u'渠道商没有进件微信, 不能使用渠道商appid')


# 判断D0提现手续费符合不符合要求
def range_fee(form, field):
    father_id = None

    if not form.father_name.data:
        raise ValidationError(u'未获取到所属上级的名称')
    if form.father_name.data == 'dt':
        father_id = form.dt_id

    if not father_id:
        raise ValidationError(u'未获取到所属上级的编号')
    ret = uline_session.query(D0WithdrawPay.wx, D0WithdrawPay.alipay).filter(
        D0WithdrawPay.role_type == form.father_name.data,
        D0WithdrawPay.role == father_id
    ).first()
    # ret = db.selectSQL(
    #     "select wx, alipay from d0_withdraw_fee where role_type = %s and role = %s;",
    #     (form.father_name, father_id)
    # )

    # 两个都为空，说明没有开通D0
    if not ret:
        raise ValidationError(u'上级未开通D0')

    else:
        # 方便阅读，转成字典
        ret = {'wx': ret[0], 'alipay': ret[1]}

        # 必须上级提现手续费不为空才可以设置下级的手续费
        if field.name in ['wx', 'wx_draw_fee']:
            if form.wx.data is not None or form.wx_draw_fee.data:
                if ret['wx'] is None:
                    raise ValidationError(u'上级未开通微信的D0支付')
                else:
                    if (form.wx.data and form.wx.data < 0) or (form.wx_draw_fee.data and form.wx_draw_fee.data < 0):
                        raise ValidationError(u'微信D0代付费用不能小于0')

                    # 提现手续费不能小于上级设置的，只能大于或等于
                    if form.wx.data and form.wx.data < int(ret['wx']):
                        raise ValidationError(u'微信D0代付费用不能小于上级设置的代付费用')
                    elif form.wx_draw_fee.data and form.wx_draw_fee.data < int(ret['wx']):
                        raise ValidationError(u'微信D0代付费用不能小于上级设置的代付费用')

        if field.name in ['alipay', 'ali_draw_fee']:
            if form.alipay.data is not None or form.wx_draw_fee.data:
                if ret['alipay'] is None:
                    raise ValidationError(u'上级未开通支付宝的D0支付')
                else:
                    if (form.alipay.data and form.alipay.data < 0) or \
                            (form.ali_draw_fee.data and form.ali_draw_fee.data < 0):
                        raise ValidationError(u'支付宝D0代付费用不能小于0')
                    if form.alipay.data and form.alipay.data < int(ret['alipay']):
                        raise ValidationError(u'支付宝D0代付费用不能小于上级设置的代付费用')
                    elif form.ali_draw_fee.data and form.wx_draw_fee.data < int(ret['alipay']):
                        raise ValidationError(u'微信D0代付费用不能小于上级设置的代付费用')


def validate_draw_rate(form, field):
    data = None
    try:
        data = float(field.data)
    except:
        pass
    if isinstance(data, float):
        if data < 0.0:
            raise ValidationError(
                u'垫资费率设置错误, 需设置大于0')

    father_id = None

    if not form.father_name.data:
        raise ValidationError(u'未获取到所属上级的名称')
    if form.father_name.data == 'dt':
        father_id = form.dt_id

    if not father_id:
        raise ValidationError(u'未获取到所属上级的编号')

    ret = uline_session.query(D0WithdrawPay.wx, D0WithdrawPay.alipay).filter(
        D0WithdrawPay.role_type == form.father_name.data,
        D0WithdrawPay.role == father_id
    ).first()

    # 两个都为空，说明没有开通D0
    if not ret:
        raise ValidationError(u'上级未开通D0')

    else:

        # 必须上级提现手续费不为空才可以设置下级的手续费
        if field.name in ['wx_draw_rate']:
            if form.wx_draw_rate.data is not None:
                # 查询渠道商d0垫资费
                ret = uline_session.query(DtPayment.withdraw_rate).filter(
                                          DtPayment.uline_payment_code.like('WX%'),
                                          DtPayment.dt_id == father_id,
                                          DtPayment.payment_rate > 0
                                        ).first()
                if ret[0] is None:
                    raise ValidationError(u'上级未开通D0')
                else:
                    # 提现手续费不能小于上级设置的，只能大于或等于
                    if form.wx_draw_rate.data and form.wx_draw_rate.data < int(ret[0]):
                        raise ValidationError(u'微信D0提现垫资费率不能小于上级设置的垫资费率')

        if field.name in ['ali_draw_rate']:
            if form.ali_draw_rate.data is not None:
                # 查询渠道商d0垫资费
                ret = uline_session.query(DtPayment.withdraw_rate).filter(
                                          DtPayment.uline_payment_code.like('ALI%'),
                                          DtPayment.dt_id == father_id,
                                          DtPayment.payment_rate > 0
                                        ).first()
                if ret[0] is None:
                    raise ValidationError(u'上级未开通D0')
                else:
                    # 提现手续费不能小于上级设置的，只能大于或等于
                    if form.ali_draw_rate.data and form.ali_draw_rate.data < int(ret[0]):
                        raise ValidationError(u'支付宝D0提现垫资费率不能小于上级设置的垫资费率')


def validate_payment_rate(form, field):
    payment_type = re.search(r'(\d+)', field.name).groups()
    if not payment_type:
        # 为空说明前端页面没有按要求写dom元素的name
        raise ValidationError(u'费率类型错误')
    # 不为空就一定有第0个数据
    payment_type = int(payment_type[0])
    payment_name = AVAILABLE_PAYMENTS[str(payment_type)]

    if not 0 <= field.data < 10000:
        raise ValidationError(u'{}的费率为0~1000'.format(payment_name))  # 1000为迎合网页需求
    # 如果新的进件，且 payment_type大于100
    d0 = False
    if FEATURE_SWITCH.get('NEW_INLET') and payment_type > 100:
        d0 = True
        payment_type -= 100

    # 应产品经理需求，目前只要渠道商判断是否有添加这个支付类型
    dt_payment = uline_session.query(DtPayment).filter(DtPayment.dt_id == form.dt_id,
                                                       DtPayment.payment_type == int(payment_type)).first()
    # DtPayment.activated_status.in_([2, 3])).first()

    if dt_payment is None:
        raise ValidationError(u'渠道商没有设置{}的费率'.format(payment_name))
    else:
        dt_user = DtUser.get_by(dt_id=form.dt_id).first()
        if dt_payment.payment_rate > field.data:
            raise ValidationError(u'不能低于渠道商设置{}的费率'.format(payment_name))
        if FEATURE_SWITCH.get('NEW_INLET'):
            # 如果是新的进件，且 payment_type大于100
            if d0 and dt_payment.payment_rate + dt_payment.withdraw_rate > field.data:
                raise ValidationError(u'不能低于渠道商设置{}的费率'.format(payment_name))
        elif dt_user.rate == 1 and float(field.data) > 0.0 and payment_type in [1, 2, 3]:
            raise ValidationError(u'0费率商户{}费率必须等于0'.format(payment_name))


def validate_license_period(form, field):
    if not (form.license_end_date.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')


def validate_license_end_date(form, field):
    if not (form.license_period.data or field.data):
        raise ValidationError(u'营业执照无效的结束时间')
    today = date.today()
    if field.data and (field.data - today).days < 90:
        raise ValidationError(u'营业执照有效期不足3个月')


def validate_bank_no(form, field):
    bank_no = BalanceBankInfo.validate_bank_no(field.data)
    if not bank_no:
        raise ValidationError(u'请输入有效的支行联行号')


def is_has_space(form, field):
    if ' ' in field.data:
        raise ValidationError(field.data + u' 包含空格, 请修改！')


def validate_industry_code(form, field):
    industry_no = UlineIndustryInfo.get_industry_code(industry_code=field.data)
    if not industry_no:
        raise ValidationError(u'无效行业类型')


def validate_dt_sub_id(form, field):
    """子账户必须属于该渠道商, 且必须存在。"""
    dt_sub_id = field.data
    dt_sub_user = DtSubUser.get_by(dt_sub_id=dt_sub_id, dt_user_dt_id=form.dt_id).first()
    if not dt_sub_user:
        raise ValidationError(u'该用户不属于该渠道商')


def vaildate_cs_id(form, filed):
    cs_id = filed.data
    dt_inlet_info = DtInletInfo.get_by(dt_id=cs_id).first()
    if not dt_inlet_info or not dt_inlet_info.parent_id:
        raise ValidationError(u'无有效连锁商户')


class AddMerchantlnlet(BaseForm):
    mch_name = fields.StringField(validators=[validators.Length(
        min=2, max=40, message=u'无效商户名'), is_has_space])
    mch_shortname = fields.StringField(
        validators=[validators.Length(min=2, max=18, message=u'无效商户简称'), is_has_space])
    industry_no = fields.StringField(
        validators=[validate_industry_code, is_has_space])
    province = fields.StringField(validators=[validators.Length(
        min=2, max=32, message=u'无效省份'), is_has_space])
    city = fields.StringField(validators=[validators.Length(
        min=2, max=30, message=u'无效城市'), is_has_space])

    # district = fields.StringField(
    #     validators=[validators.Length(min=2, max=32, message=u'无效区域'), is_has_space])
    district = fields.StringField()

    address = fields.StringField(validators=[validators.Length(
        min=2, max=255, message=u'无效地址'), is_has_space])
    contact = fields.StringField(validators=[validators.Length(
        min=2, max=20, message=u'无效联系人姓名'), is_has_space])
    mobile = fields.StringField(validators=[validators.Length(
        min=11, max=11, message=u'手机号必须为11位'), is_has_space])
    service_phone = fields.StringField(
        validators=[validators.Length(min=5, max=15, message=u'无效客服电话'), is_has_space])
    email = fields.StringField(
        validators=[validators.Email(message=u'无效邮箱'), is_has_space])
    balance_type = fields.IntegerField(
        validators=[validators.NumberRange(min=1, max=2, message=u'无效结算账号类型')])
    balance_name = fields.StringField(
        validators=[validators.Length(min=1, max=255, message=u'无效结算户名'), is_has_space])
    bank_no = fields.StringField(validators=[validate_bank_no, is_has_space])
    balance_account = fields.StringField(
        validators=[validators.Length(min=9, max=23, message=u'无效结算账户'), is_has_space])
    id_card_no = fields.StringField(validators=[validators.Length(
        min=1, max=20, message=u'无效身份证号码'), is_has_space])
    activate_email_tag = fields.IntegerField(validators=[validators.Optional()])

    # 银联新字段
    # 负责人
    head_name = fields.StringField(validators=[validators.Optional(), validators.Length(
        min=2, max=20, message=u'无效负责人姓名'), is_has_space])
    # 负责人电话
    head_mobile = fields.StringField(validators=[validators.Optional(),
                                                 validators.Length(min=5, max=15, message=u'无效负责人电话'),
                                                 is_has_space])
    # 负责人类型
    head_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(["LEGAL_PERSON", "CONTROLLER", "AGENT", "OTHER"])
        ]
    )

    # 手持身份证照片
    img_with_id_card = fields.FileField(validators=[validators.Optional(), File])

    id_card_img_f = fields.FileField(validators=[File])
    id_card_img_b = fields.FileField(validators=[File])
    license_img = fields.FileField(validators=[File])

    wx_use_parent = RadioField(validators=[validators.DataRequired()], choices=[('1', '不使用'), ('2', '使用')],
                               default='1')

    payment_type1 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type2 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type3 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type4 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type5 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type7 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type8 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type9 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])

    # 京东支付
    payment_type21 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type22 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type23 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])

    # 银联
    payment_type33 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])

    # D0 的费率
    payment_type101 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type102 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type103 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type104 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type105 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type107 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type108 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type109 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])

    # D0提现手续费
    wx = fields.IntegerField(
        validators=[
            validators.Optional(),
            range_fee
        ]
    )

    alipay = fields.IntegerField(
        validators=[
            validators.Optional(),
            range_fee
        ]
    )

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
            validate_new_payment_rate
        ],
        places=1)

    JD_ONLINE_H5_DEBIT = fields.DecimalField(
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

    # 银联
    UNIONPAY_OFFLINE_JSAPI = fields.DecimalField(
        validators=[
            validators.Optional(),
            validate_new_payment_rate
        ],
        places=1)

    # D0提现手续费
    wx_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            range_fee
        ]
    )

    ali_draw_fee = fields.DecimalField(
        validators=[
            validators.Optional(),
            range_fee
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

    father_name = fields.StringField()

    notify_url = fields.StringField(
        validators=[validators.Optional(), validators.URL()])

    license_num = fields.StringField(validators=[
        validators.required(),
        validators.Length(min=1, max=32, message=u'无效营业执照注册号')
    ])
    # 营业执照类型
    license_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(['NATIONAL_LEGAL', 'NATIONAL_LEGAL_MERGE', 'INST_RGST_CTF'])
        ]
    )

    license_start_date = fields.DateField(
        validators=[validators.DataRequired()])
    license_end_date = fields.DateField(validators=[
        validators.Optional(),
        validate_license_end_date
    ])
    license_period = fields.StringField(validators=[validate_license_period])
    license_scope = fields.TextAreaField(validators=[
        validators.Length(max=500, message=u'营业范围(与企业工商营业执照上一致)')
    ])
    dt_sub_id = fields.IntegerField(validators=[validators.Optional(), validate_dt_sub_id])
    cs_id = fields.IntegerField(validators=[validators.Optional(), vaildate_cs_id])

    # 围餐相关
    use_dine = fields.StringField(validators=[validators.optional()])

    payment_type11 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type12 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])
    payment_type13 = fields.IntegerField(validators=[validators.Optional(), validate_payment_rate])

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
