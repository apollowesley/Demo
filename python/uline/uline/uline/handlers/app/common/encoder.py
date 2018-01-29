#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: LiuFei
# @createTime: 2017-09-21 10:41:45
# @description: 自定义JSON转换器

import json
from datetime import datetime
from decimal import Decimal


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return "%.2f" % obj
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)
