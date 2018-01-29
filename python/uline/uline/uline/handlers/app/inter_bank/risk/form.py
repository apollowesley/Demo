from wtforms import validators, fields
from uline.utils.form import BaseForm


class MerchantRiskSearchForm(BaseForm):
    has_risk = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([0, 1, 2])], default=0)
    risk_type = fields.StringField(validators=[validators.Optional(),
                                               validators.AnyOf(['cert_no', 'bank_card_no', 'business_license_no'])])
    risk_content = fields.StringField(validators=[validators.Optional()])


class MerchantRiskDetailForm(BaseForm):
    risk_id = fields.IntegerField(validators=[validators.DataRequired()])


class TradeRiskSearchForm(BaseForm):
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    handle_status = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([0, 1, 2, 3])], default=0)
    merchant_id = fields.IntegerField(validators=[validators.Optional()])
    merchant_name = fields.StringField(validators=[validators.Optional()])
    merchant_shortname = fields.StringField(validators=[validators.Optional()])
    dt_id = fields.IntegerField(validators=[validators.Optional()])
    dt_name = fields.StringField(validators=[validators.Optional()])


class TradeRiskDealForm(BaseForm):
    handle_type = fields.StringField(validators=[validators.AnyOf(['deal', 'ignore'])])
    risk_id = fields.IntegerField(validators=[validators.DataRequired()])
    close_payments = fields.StringField(validators=[validators.Optional()])
    freeze_account = fields.StringField(validators=[validators.Optional()])


class TradeRiskDetailForm(BaseForm):
    risk_id = fields.IntegerField(validators=[validators.DataRequired()])


class RiskControlSettleForm(BaseForm):
    role_id = fields.IntegerField(validators=[validators.DataRequired()])
    role_type = fields.StringField(validators=[validators.DataRequired()])
    action = fields.StringField(validators=[validators.DataRequired(), validators.AnyOf(['close', 'open'])])


class RiskControlCreditForm(BaseForm):
    platform = fields.StringField(validators=[validators.Optional(), validators.AnyOf(['weixin', 'alipay'])])
    role_id = fields.IntegerField(validators=[validators.DataRequired()])
    role_type = fields.StringField(validators=[validators.DataRequired()])
    action = fields.StringField(validators=[validators.DataRequired(), validators.AnyOf(['close', 'open'])])


class GetMerchantPaymentsForm(BaseForm):
    merchant_id = fields.IntegerField(validators=[validators.DataRequired()])
