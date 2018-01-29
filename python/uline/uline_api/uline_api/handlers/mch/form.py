#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '12/14/16'

from __future__ import division
from wtforms import ValidationError
from wtforms.validators import data_required
from wtforms import fields
from uline_api.util.form import BaseForm
from uline_api.model.uline.info import MchInletInfo


def validate_mch_id(form, field):
    mch_id = field.data
    if not mch_id.isdigit():
        raise ValidationError(u'mch_id必须是数字')

    mchinletinfo = MchInletInfo.get_by(dt_id=form.dt_id, mch_id=mch_id).first()
    if mchinletinfo is None:
        raise ValidationError(u'mch_id不存在')


class MerchantBaseForm(BaseForm):
    mch_id = fields.StringField(validators=[data_required(message=u'必须传入商户号mch_id'), validate_mch_id])


class GetMCHPayKey(MerchantBaseForm):
    pass


class MerchantForm(MerchantBaseForm):
    pass
