#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

import re
from tornado import escape
from wtforms import ValidationError, Form


class BaseForm(Form):
    class Meta:
        locales = ['zh']

    def __init__(self, handler, obj=None, prefix='', **kwargs):
        # TODO 目前只处理了request.query_arguments和request.arguments
        formdata = MultiDict()
        if handler.request.method == 'POST':
            for name in handler.request.arguments.keys():
                formdata.setlist(name, handler.get_arguments(name))
        else:
            for name in handler.request.query_arguments.keys():
                formdata.setlist(name, handler.request.query_arguments[name])
        Form.__init__(self, formdata, obj=obj, prefix=prefix, **kwargs)


class BaseInletForm(Form):
    class Meta:
        locales = ['zh']

    def __init__(self, handler, obj=None, prefix='', **kwargs):
        formdata = MultiDict()
        for name in handler.keys():
            formdata.setlist(name, [str(handler[name])])
        Form.__init__(self, formdata, obj=obj, prefix=prefix, **kwargs)


class MultiDict(dict):

    def getlist(self, key):
        return self[key]

    def setlist(self, key, value):
        self[key] = value

    def __repr__(self):
        return type(self).__name__ + '(' + dict.__repr__(self) + ')'


def File(form, field):
    if not field.raw_data:
        raise ValidationError(u"上传文件不能为空")
    filename = field.raw_data[0].filename if field.raw_data[0] else None
    if not filename:
        raise ValidationError(u"上传文件不能为空")


def IdCard(form, field):
    # 身份证验证
    chmap = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, 'x': 10, 'X': 10
    }

    def verify_list(l):
        sum = 0
        for ii, n in enumerate(l):
            i = 18 - ii
            weight = 2 ** (i - 1) % 11
            sum = (sum + n * weight) % 11
        return sum == 1
    char_list = list(field.data)
    num_list = [chmap[ch] for ch in char_list]
    if not verify_list(num_list):
        raise ValidationError(u'请输入正确的身份证号')


def is_has_space(form, field):
    """验证字段是否有空格"""
    if re.search(r' ', str(field.data)):
        raise ValidationError(str(field.data) + u' 包含空格, 请修改！')


def validate_phone(form, field):
    """验证手机号码是否符合正常的格式"""
    if not (re.match(r'1\d{10}', str(field.data))):
        raise ValidationError(u'手机号码%s无效, 请修改!' % str(field.data))


class SecondBaseForm(Form):

    def __init__(self, handler, obj=None, prefix='', **kwargs):

        formdata = MultiDict()
        if handler.request.method == 'POST':
            for name in escape.json_decode(handler.request.body).keys():
                formdata.setlist(name, [str(escape.json_decode(handler.request.body)[name])])
        else:
            for name in handler.request.query_arguments.keys():
                formdata.setlist(name, handler.request.query_arguments[name])
        Form.__init__(self, formdata, obj=obj, prefix=prefix, **kwargs)
