#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import decimal
import json


def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.
    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None


class LazableJSONEncoder(json.JSONEncoder):
    """
    JSON serializable datetime.datetime
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError('JSON can\'t represent timezone-aware times.')
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(LazableJSONEncoder, self).default(o)


class DateJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, datetime.timedelta):
            obj_str = str(obj)
            return obj_str
        else:
            return json.JSONEncoder.default(self, obj)
