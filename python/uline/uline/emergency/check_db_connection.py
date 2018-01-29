#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.backend.__init__ import *
from uline.public import log
import datetime
from uline.settings import env


def get_current_connections():
    nums = db.selectSQL('SELECT count(datid) FROM pg_stat_activity;')
    return nums[0]


def get_detail_connections():
    details = db.selectSQL(
        'select count(datid), client_addr from pg_stat_activity GROUP BY client_addr;', fetchone=False)
    for nums, name in details:
        log.uline_script.info('name:%s|count:%s' % (name, nums))


def main():
    nums = get_current_connections()
    log.uline_script.info('now:%s | current_connections:%s' % (datetime.datetime.now(), nums))
    # 超过300，发送邮件告警
    if nums > 300:
        import json
        import requests
        if env == 'SPD_PROD':
            data = {
                'env': 'SPD_PROD',
                'reciver': '312736700@qq.com',
                'title': u'env:%s | 数据库连接数超过300,请查看' % env,
                'body': u'当前数据库连接:%s' % nums,

            }
            url = 'http://127.0.0.1:6789' + '/v1/email'
        else:
            data = {
                'env': 'CMBC_PROD',
                'reciver': '17721246491',
                'body': u'您的验证码是300300,一个小时后失效。'
            }
            url = 'http://127.0.0.1:6789' + '/v1/message'
        requests.post(url, data=json.dumps(data))
    get_detail_connections()


if __name__ == "__main__":
    main()
