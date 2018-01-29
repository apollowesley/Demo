#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
import datetime
import argparse
from tornado.httpclient import HTTPClient
from uline.config.base import MESSAGE_URL
from uline.settings import env
from uline.public import log


def get_base_url():
    """从命令行获取检测的url路径"""
    parser = argparse.ArgumentParser(description='Process url.')
    parser.add_argument('base_url', metavar='BASE_URL', type=str,
                        help='input base_url')
    args = parser.parse_args()
    return args.dt_id


def health_check(url):
    count = 0
    http_client = HTTPClient()
    for i in range(31):
        try:
            response = http_client.fetch(url, connect_timeout=2, request_timeout=2)
            # if response and response.body == b'2':
            if response:
                pass
            else:
                count += 1
        except:
            count += 1
        time.sleep(5)
    return count


def send_alarm_email(base_count, static_count):
    http_client = HTTPClient()
    data = {
        'env': env,
        'reciver': '312736700@qq.com',
        'title': u'%s:uline系统10分钟内调用失败次数%s, 静态文件失败次数：%s' % (env, base_count, static_count),
        'body': u'uline系统10分钟内调用失败次数%s, 静态文件失败次数：%s' % (base_count, static_count),
    }
    url = MESSAGE_URL + '/v1/email'

    for i in range(3):
        response = http_client.fetch(url, body=json.dumps(data), method='POST')
        if response.body == '1':
            time.sleep(50)
        else:
            break


def main():
    """
    获取检测url
    """
    log.uline_script.info('health check time: %s ' % datetime.datetime.now())
    base_url = get_base_url()
    # base_url = 'http://cms.spd.uline.cc/'
    # static_url = 'http://cms.spd.uline.cc/static/favicon.ico'
    static_url = base_url + 'static/favicon.ico'

    base_count = health_check(base_url)
    static_count = health_check(static_url)

    log.uline_script.info('base_url_count fail:%s' % base_count)
    log.uline_script.info('static_url_count fail:%s' % static_count)

    if base_count >= 2 or static_count >= 2:
        log.uline_script.info('send_alarm_email, time:%s' % datetime.datetime.now())
        send_alarm_email(base_count, static_count)


if __name__ == '__main__':
    main()
