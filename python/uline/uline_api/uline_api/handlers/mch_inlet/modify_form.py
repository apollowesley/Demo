# -*- coding: utf-8 -*-
from __future__ import division
import re
from datetime import date


from wtforms import ValidationError
from wtforms import validators, fields, RadioField

from uline_api.model.uline.info import BalanceBankInfo, UlineIndustryInfo, DtPayment
from uline_api.model.uline.user import DtUser
from uline_api.public.constants import NEW_AVAILABLE_PAYMENTS
from uline_api.model.uline.base import uline_session
from uline_api.util.form import BaseForm, IdCard, File, UlineAnyOf
from .form import validate_payment_rate, validate_dt_sub_id, range_fee, validate_draw_rate


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

    # # 支付宝线上费率不得低于千2
    # if platform == 'ALI' and channel == 'OFFLINE' and isinstance(data, float) and data < 20:
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

def is_has_space(form, field):
    if ' ' in field.data:
        raise ValidationError(field.data + u' 包含空格, 请修改！')


def validate_bank_no(form, field):
    bank_no = BalanceBankInfo.validate_bank_no(field.data)
    if not bank_no:
        raise ValidationError(u'请输入有效的支行联行号')


def validate_industry_code(form, field):
    industry_no = UlineIndustryInfo.get_industry_code(industry_code=field.data)
    if not industry_no:
        raise ValidationError(u'无效行业类型')


def validate_license_period(form, field):
    if form.license_end_date.data is None and field.data in [None, False]:
        raise ValidationError(u'无效的结束时间')


def validate_license_end_date(form, field):
    if form.license_period.data in [None, False] and field.data is None:
        raise ValidationError(u'无效的结束时间')
    today = date.today()
    if (field.data - today).days < 90:
        raise ValidationError(u'有效期不足3个月')


class UpdateMerchantlnletForm(BaseForm):
    mch_name = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=2, max=40, message=u'无效商户名')
        ]
    )
    mch_shortname = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=2, max=18, message=u'无效商户简称')
        ]
    )
    industry_no = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=15, max=15, message=u'无效经营类目ID'),
            validate_industry_code
        ]
    )
    province = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=2, max=32, message=u'无效省份')
        ]
    )
    city = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=2, max=32, message=u'无效城市')
        ]
    )
    district = fields.StringField()
    # district = fields.StringField(
    #     validators=[
    #         validators.Optional(),
    #         validators.Length(min=2, max=32, message=u'无效区域')
    #     ]
    # )
    address = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=2, max=255, message=u'无效地址')
        ]
    )

    contact = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=2, max=20, message=u'无效联系人姓名')
        ]
    )

    mobile = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=11, max=11, message=u'手机号必须为11位')
        ]
    )

    service_phone = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=5, max=15, message=u'无效客服电话')
        ]
    )

    email = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Email(message=u'无效邮箱')
        ]
    )

    balance_type = fields.IntegerField(
        validators=[
            validators.Optional(),
            validators.NumberRange(min=1, max=2, message=u'无效结算账号类型')
        ]
    )

    balance_name = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=1, max=255, message=u'无效结算户名')
        ]
    )

    bank_no = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=12, max=13, message=u'无效支行联行号'),
            validate_bank_no
        ]
    )

    balance_account = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=9, max=23, message=u'无效结算账户')
        ]
    )

    id_card_no = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=1, max=20, message=u'无效身份证号码'),
        ]
    )

    notify_url = fields.StringField(
        validators=[
            validators.Optional(),
            validators.Length(min=9, max=180, message=u'URL长度最短为9,最长为180'),
            validators.URL(message=u'请输入有效URL')
        ]
    )

    id_card_img_f = fields.FileField('id_card_img_f', validators=[validators.Optional(), File])
    id_card_img_b = fields.FileField('id_card_img_b', validators=[validators.Optional(), File])


    # 银联新字段
    # 负责人
    head_name = fields.StringField(validators=[validators.Optional(), validators.Length(
        min=2, max=20, message=u'无效负责人姓名'), is_has_space])
    # 负责人电话
    head_mobile = fields.StringField(validators=[validators.Optional(),
                                                 validators.Length(min=5, max=15, message=u'负责人电话'),
                                                 is_has_space])
    # 负责人类型
    head_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(["LEGAL_PERSON", "CONTROLLER", "AGENT", "OTHER"])
        ]
    )

    # 手持身份证照片
    img_with_id_card = fields.FileField('img_with_id_card', validators=[validators.Optional(), File])

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

    # 银联
    UNIONPAY_OFFLINE_JSAPI = fields.DecimalField(
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

    license_num = fields.StringField(
        validators=[validators.Optional(), validators.Length(min=1, max=32, message=u'无效营业执照注册号')]
    )
    # 营业执照类型
    license_type = fields.StringField(
        validators=[
            validators.Optional(),
            validators.AnyOf(['NATIONAL_LEGAL', 'NATIONAL_LEGAL_MERGE', 'INST_RGST_CTF'])
        ]
    )

    license_start_date = fields.DateField(validators=[validators.Optional()])
    license_end_date = fields.DateField(validators=[validators.Optional(), validate_license_end_date])
    license_period = fields.BooleanField('licensePeriod', validators=[validate_license_period])
    license_scope = fields.TextAreaField(
        validators=[validators.Optional(), validators.Length(min=1, max=500, message=u'营业范围(与企业工商营业执照上一致)')]
    )
    license_img = fields.FileField('licenseImg', validators=[validators.Optional(), File])
    dt_sub_id = fields.IntegerField(validators=[validators.Optional(), validate_dt_sub_id])
    industry_no = fields.StringField(validators=[validators.Optional(), validate_industry_code, is_has_space])
    wx_use_parent = RadioField(validators=[validators.DataRequired()], choices=[('1', '不使用'), ('2', '使用')],
                               default='1')

    cs_id = fields.StringField()

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

    # 删除哪些进件补充材料的图片
    # 字符串形式，用数字和-代表需要删除哪些图片，如：1  1-3  1-3-5
    del_annex = fields.StringField(validators=[validators.optional()])

    # 围餐补充材料图片
    wx_dine_annex_img1 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img2 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img3 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img4 = fields.FileField(validators=[validators.optional(), File])
    wx_dine_annex_img5 = fields.FileField(validators=[validators.optional(), File])

    # 删除哪些进件补充材料的图片
    # 字符串形式，用数字和-代表需要删除哪些图片，如：1  1-3  1-3-5
    del_wx_dine_annex = fields.StringField(validators=[validators.optional()])


class SetMchWxPayConfigForm(BaseForm):
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
        ]
    )

    config_key = fields.StringField(validators=[UlineAnyOf(['subscribe_appid', 'sub_appid', 'jsapi_path'])])

    config_value = fields.StringField(validators.DataRequired(message=u'需要填写配置参数的值'))

    config_channel = fields.StringField(validators=[UlineAnyOf(['reg_online', 'reg_offline', 'dine'])])

    mch_type = fields.StringField(validators=[UlineAnyOf(['mch', 'chain'])], default='mch')


class GetMchWxPayConfigForm(BaseForm):
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
        ]
    )

    config_channel = fields.StringField(validators=[UlineAnyOf(['reg_online', 'reg_offline', 'dine'])])

    mch_type = fields.StringField(validators=[UlineAnyOf(['mch', 'chain'])], default='mch')


class UpdateMchWxPayConfigForm(BaseForm):
    mch_id = fields.IntegerField(
        validators=[
            validators.DataRequired(message=u'查询字符不能为空'),
        ]
    )

    mch_type = fields.StringField(validators=[UlineAnyOf(['mch', 'chain'])], default='mch')
