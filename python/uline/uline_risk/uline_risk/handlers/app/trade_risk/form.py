from wtforms import validators, fields, Form
from uline_risk.utils.form import BaseForm


class TradeRiskDealForm(Form):
    handle_type = fields.StringField(validators=[validators.AnyOf(['deal', 'ignore'])])
    risk_id = fields.IntegerField(validators=[validators.DataRequired()])
    close_payments = fields.StringField(validators=[validators.Optional()])
    freeze_account = fields.StringField(validators=[validators.Optional()])
    operator_id = fields.IntegerField(validators=[validators.Optional()])
    operator_type = fields.StringField(validators=[validators.Optional()])
    operator_email = fields.StringField(validators=[validators.Optional()])
    operator_name = fields.StringField(validators=[validators.Optional()])


class QueyTradeRiskForm(BaseForm):
    risk_id = fields.IntegerField(validators=[validators.Optional()])
    bk_id = fields.FieldList(fields.IntegerField(validators=[validators.Optional()]))
    create_at_start = fields.DateField(validators=[validators.Optional()])
    create_at_end = fields.DateField(validators=[validators.Optional()])
    handle_status = fields.IntegerField(validators=[validators.Optional(), validators.AnyOf([0, 1, 2, 3])], default=0)
    merchant_id = fields.IntegerField(validators=[validators.Optional()])
    merchant_name = fields.StringField(validators=[validators.Optional()])
    merchant_shortname = fields.StringField(validators=[validators.Optional()])
    dt_id = fields.IntegerField(validators=[validators.Optional()])
    dt_name = fields.StringField(validators=[validators.Optional()])
    page = fields.IntegerField(validators=[validators.Optional()])
    page_size = fields.IntegerField(validators=[validators.Optional()])


class AddTradeRiskForm(BaseForm):
    pass
