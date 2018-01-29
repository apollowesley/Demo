#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '3/8/17'

# 检测config目录下面是不是都相等的

import os
import importlib

config_dir = os.path.join(os.getcwd(), 'uline_api/config')


def check():
    compare_result = {}
    for env in os.listdir(config_dir):
        if env.startswith('_') or env == 'base':
            continue
        model = importlib.import_module('uline_api.config.{}.conf'.format(env))
        compare_result[env] = list(sorted(i for i in dir(model) if not i.startswith('_')))

    for i in compare_result:
        if compare_result[i] != compare_result['local']:
            difference = list(set(compare_result["local"]) - set(compare_result[i])) or list(
                set(compare_result[i]) - set(compare_result["local"]))
            raise Exception(u'配置中{}和local不同,不同的项为{}'.format(i, difference))
