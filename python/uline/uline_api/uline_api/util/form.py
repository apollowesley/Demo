#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/9/16'

import tornado
import tornado.escape
from wtforms import ValidationError, Form
from wtforms.validators import AnyOf


class BaseForm(Form):

    def __init__(self, handler=None, obj=None, prefix='', **kwargs):
        # TODO 目前只处理了request.query_arguments和request.arguments
        if handler is None:
            return
        formdata = MultiDict()
        if handler.request.method == 'POST':
            for name in handler.request.arguments.keys():
                formdata.setlist(name, handler.get_arguments(name))
        else:
            try:
                data = tornado.escape.json_decode(handler.request.body)
            except:
                data = handler.request.query_arguments

            for name in data.keys():
                formdata.setlist(name, handler.request.query_arguments[name])
        super(BaseForm, self).__init__(
            formdata, obj=obj, prefix=prefix, **kwargs)


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
    if isinstance(field.raw_data[0], str):
        raise ValidationError(u"上传图片必须是文件类型")
    filename = field.raw_data[0].filename if field.raw_data[0] else None
    if not filename:
        raise ValidationError(u"上传文件不能为空")


def IdCard(form, field):
    # 身份证验证
    chmap = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, 'x': 10, 'X': 10
    }
    for i in field.data:
        if i not in chmap:
            raise ValidationError(u'请输入正确的身份证号')

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


class UlineAnyOf(AnyOf):

    def __call__(self, form, field):
        if field.data not in self.values:
            message = self.message
            if message is None:
                message = field.gettext(u'{}参数无效, 参数值必须是以下之一: %(values)s.'.format(field.name))

            raise ValidationError(message % dict(values=self.values_formatter(self.values)))
