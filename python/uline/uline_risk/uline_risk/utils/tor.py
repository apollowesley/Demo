#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '2/21/17'


# 出自 https://gist.github.com/Hackforid/7130a5d59463186e217e

import threading


class classproperty(property):
    def __get__(self, obj, objtype=None):
        return super(classproperty, self).__get__(objtype)

    def __set__(self, obj, value):
        super(classproperty, self).__set__(type(obj), value)

    def __delete__(self, obj):
        super(classproperty, self).__delete__(type(obj))


class ThreadRequestContext(object):
    """A context manager that saves some per-thread state globally.
    Intended for use with Tornado's StackContext.
    Provide arbitrary data as kwargs upon creation,
    then use ThreadRequestContext.data to access it.
    """

    _state = threading.local()
    _state.data = {}

    @classproperty
    def data(cls):
        if not hasattr(cls._state, 'data'):
            return {}
        return cls._state.data

    def __init__(self, **data):
        self._data = data

    def __enter__(self):
        self._prev_data = self.__class__.data
        self.__class__._state.data = self._data

    def __exit__(self, *exc):
        self.__class__._state.data = self._prev_data
        del self._prev_data
        return False


# def get_current_request_id():
#     return ThreadRequestContext.data['request_id']

def get_current_request_id():
    """
    """
    unique_id = ThreadRequestContext.data.get('request_id')
    # 如果request_id为空， 则可能处于新的线程里面
    if not unique_id:
        unique_id = ThreadRequestContext.data.get('thread_id')
    return unique_id
