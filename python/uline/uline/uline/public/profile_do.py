#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import os
import cProfile
import pstats
import urlparse
from urllib import urlencode

import functools
from tornado.httpclient import HTTPError


def profile(function):
    def _profile(*args, **kwargs):
        s = tempfile.mktemp()
        profiler = cProfile.Profile()
        profiler.runcall(function, *args, **kwargs)
        profiler.dump_stats(s)
        p = pstats.Stats(s)
        p.sort_stats("time").print_stats(6)
        return function(*args, **kwargs)
    return _profile


def pro(method):

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        s = tempfile.mktemp()
        profiler = cProfile.Profile()
        profiler.runcall(method, self, *args, **kwargs)
        profiler.dump_stats(s)
        p = pstats.Stats(s)
        p.sort_stats("time").print_stats(6)
        return method(self, *args, **kwargs)
    return wrapper
