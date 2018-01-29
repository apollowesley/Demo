#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wtforms import validators, fields
from uline.utils.form import BaseForm


class MessageSendSearch(BaseForm):
    create_at = fields.DateTimeField(validators=[validators.Optional()])
    message_content = fields.StringField(validators=[validators.Optional()])
    sended_count = fields.IntegerField(
        validators=[validators.Optional()])  # 已发送的条数
    need_send_count = fields.IntegerField(
        validators=[validators.Optional()])  # 为发送的条数
