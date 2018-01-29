# -*- coding:utf-8 -*-
import concurrent.futures
import datetime
import json
import random
import string
import time
# 用户认证
from random import choice

from .baseDB import DbClient

db = DbClient()


######################
# handler 常用工具
######################

# 初始化 response
def generate_rsp(return_code=10000, return_msg="success", result_code=10000, result_msg="success", **kwargs):
    rsp = {'return_code': return_code, 'return_msg': return_msg, 'result_code': result_code, 'result_msg': result_msg}
    rsp.update(kwargs)
    return rsp


# json 封装 response 字典 并兼容中文（类似 \x70s）


def json_dumps_ensure_chinese(DictInfo):
    return json.dumps(DictInfo, ensure_ascii=False)


# 返回当前时间
def current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


# 生成随机密码


def generate_password(length):
    pwd = ''.join(
        random.choice(string.ascii_letters) if random.random(
        ) > 0.5 else random.choice(string.ascii_letters).upper()
        for _ in range(length))
    return pwd


executor = concurrent.futures.ThreadPoolExecutor(2)


def timestamp_now():
    return datetime.datetime.now()


def get_today_range(format='%Y-%m-%d %H:%M:%S'):
    now = datetime.datetime.now()
    today_start = now.strftime("%Y-%m-%d 00:00:00")
    today_end = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    # return datetime, datetime
    return datetime.datetime.strptime(today_start, format), datetime.datetime.strptime(today_end, format)


def get_week_range(format='%Y-%m-%d'):
    now = datetime.datetime.now()
    today_end = now.strftime(format)
    today_start = (now - datetime.timedelta(days=6)).strftime(format)
    # return datetime, datetime
    return datetime.datetime.strptime(today_start, format).date(), datetime.datetime.strptime(today_end, format).date()


def get_month_range(format='%Y-%m-%d %H:%M:%S'):
    now = datetime.datetime.now()
    today_end = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    today_start = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%d 00:00:00")
    # return datetime, datetime
    return datetime.datetime.strptime(today_start, format), datetime.datetime.strptime(today_end, format)


def append_start_end(details, query_date):
    detail = list()
    if int(query_date) == 2:
        for i in details:
            j = list(i)
            _year, _month = j[0].split('-')[:2]
            next_month = 1 if int(_month) == 12 else int(_month) + 1
            next_year = int(_year) + 1 if int(_month) == 12 else int(_year)
            days = (datetime.datetime(next_year, next_month, 1) -
                    datetime.datetime(int(_year), int(_month), 1)).days
            end_date = datetime.datetime(int(_year), int(
                _month), days, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')
            start_date = datetime.datetime(int(_year), int(
                _month), 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
            j.extend([start_date, end_date])
            detail.append(tuple(j))
    else:
        for i in details:
            j = list(i)
            # kk = (parse_ymd(j[0]) + datetime.timedelta(1)).strftime("%Y-%m-%d")
            kk = (parse_ymd(j[0])).strftime("%Y-%m-%d")
            _year, _month, _day = str(kk).split('-')
            end_date = datetime.datetime(int(_year), int(
                _month), int(_day), 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')
            start_date = datetime.datetime(int(_year), int(_month), int(
                _day), 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
            j.extend([start_date, end_date])
            detail.append(tuple(j))
    return detail


def parse_ymd(s):
    year_s, mon_s, day_s = s.split('-')
    return datetime.datetime(int(year_s), int(mon_s), int(day_s))


def get_date_range(create_at_start, create_at_end):
    count = (datetime.datetime.strptime(str(create_at_end), "%Y-%m-%d") -
             datetime.datetime.strptime(str(create_at_start), "%Y-%m-%d")).days
    create_at_end_date = datetime.datetime.strptime(
        str(create_at_end), "%Y-%m-%d")
    return [datetime.datetime.strftime(create_at_end_date - datetime.timedelta(i), "%Y-%m-%d") for i in
            range(count + 1)]


def gen_random_str(min_length=30, max_length=30, allowed_chars=(string.ascii_letters + string.digits)):
    if min_length == max_length:
        length = min_length
    else:
        length = choice(range(min_length, max_length))

    return ''.join([choice(allowed_chars) for i in range(length)])


def datetime_to_str(date_obj, format="%Y-%m-%d %H:%M:%S"):
    if not date_obj:
        return ''
    return date_obj.strftime(format)
