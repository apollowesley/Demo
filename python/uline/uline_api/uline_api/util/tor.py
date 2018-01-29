#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '2/21/17'


# 出自 https://gist.github.com/Hackforid/7130a5d59463186e217e

import threading


class Metaclass(type):
    # property() doesn't work on classmethods,
    #  see http://stackoverflow.com/q/128573/1231454

    @property
    def data(cls):
        if not hasattr(cls._state, 'data'):
            return {}
        return cls._state.data


class ThreadRequestContext(object):

    __metaclass__ = Metaclass

    """A context manager that saves some per-thread state globally.
    Intended for use with Tornado's StackContext.
    Provide arbitrary data as kwargs upon creation,
    then use ThreadRequestContext.data to access it.
    """

    _state = threading.local()
    _state.data = {}

    def __init__(self, **data):
        self._data = data

    def __enter__(self):
        self._prev_data = self.__class__.data
        self.__class__._state.data = self._data

    def __exit__(self, *exc):
        self.__class__._state.data = self._prev_data
        del self._prev_data
        return False


def get_current_request_id():
    return ThreadRequestContext.data['request_id']
