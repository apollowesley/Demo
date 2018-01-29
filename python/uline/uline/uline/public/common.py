# -*- coding:utf-8 -*-
import tornado
import tornado.escape
import json
import random
import string
import time
# 用户认证
import bcrypt
from random import choice
import tornado.gen
from uline.public import log
import concurrent.futures
from .baseDB import DbClient
import os
import codecs
import datetime
from hashlib import md5
import sys
from tornado.httpclient import AsyncHTTPClient
from uline.settings import ULINE_API_URL
from collections import defaultdict
from tornado import gen
from uline.public.constants import FEATURE_SWITCH
db = DbClient()


######################
# handler 常用工具
######################

# 初始化 response
def scc_rsp(code=200, msg='ok', **args):
    rsp = {'msg': msg, 'code': code, 'INTER_BANK': FEATURE_SWITCH.get("INTER_BANK")}
    if args:
        if isinstance(args, dict):
            rsp['data'] = args
    return rsp


def f_rsp(code=500, msg='Server Error', **kwargs):
    rsp = {'msg': msg, 'code': code, 'INTER_BANK': FEATURE_SWITCH.get("INTER_BANK")}
    for k in kwargs:
        rsp[k] = kwargs[k]
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


@tornado.gen.coroutine
def bcrypt_pwd(pwd, validate=None):
    # 使用bcrypt生成安全的密码,且支持验证
    if not validate:
        hashed_password = yield executor.submit(bcrypt.hashpw, tornado.escape.utf8(pwd), bcrypt.gensalt())
        raise tornado.gen.Return(hashed_password)
    else:
        authentication = yield executor.submit(
            bcrypt.checkpw, tornado.escape.utf8(pwd), tornado.escape.utf8(validate))
        raise tornado.gen.Return(authentication)


def bcrypt_pwd_block(pwd, validate=None):
    # 使用bcrypt生成安全的密码,且支持验证
    if not validate:
        hashed_password = bcrypt.hashpw(tornado.escape.utf8(pwd), bcrypt.gensalt())
        return hashed_password
    else:
        authentication = bcrypt.checkpw(tornado.escape.utf8(pwd), tornado.escape.utf8(validate))
        return authentication


def bcrypt_pwd_new(pwd):
    return bcrypt.hashpw(pwd, bcrypt.gensalt())


def create_mch_id():
    incr_id = db.selectSQL("select nextval('tb_mch_id_seq')")
    mch_id = int(str(incr_id[0]) + str(random.randint(10, 99)))
    return mch_id


def create_bk_id():
    incr_id = db.selectSQL("SELECT max(bk_id) + 1 from bk_user")
    if incr_id:
        if isinstance(incr_id, tuple):
            incr_id = int(incr_id[0])
    else:
        incr_id = 10000000
    return incr_id


def create_dt_id():
    incr_id = db.selectSQL("select nextval('tb_dt_id_seq')")
    dt_id = int(str(incr_id[0]) + str(random.randint(100, 999)))
    return dt_id


def create_ub_id():
    incr_id = db.selectSQL("select nextval('tb_ub_id_seq')")
    ub_id = int(str(incr_id[0]) + str(random.randint(100, 999)))
    return ub_id


def create_order_id(len=32):
    return codecs.encode(os.urandom(len), 'hex').decode()[:len]


def gen_randown_mch_pkey(len=32):
    return codecs.encode(os.urandom(len), 'hex').decode()[:len]


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


def decode(fields, value, md5_sign=False):
    # 将字符串修改为GBK编码,绝对禁止value的长度比fields长
    # field = [ 10, 100 , 10 ...]
    # 返回unicode,发送前使用encode('GBK')再发送
    value = [i.encode('GBK') if isinstance(i, unicode) else str(
        i).decode('UTF-8').encode('GBK') for i in value]
    for field, v in zip(fields, value):
        if len(v) > int(field):
            log.exception.info(u'绝对禁止发送长度大于定义长度,{}:{}'.format(field, v))
            sys.exit(1)

    message = ''.join(v + ' ' * (length - len(v))
                      for length, v in zip(fields, value))
    if md5_sign:
        sign = md5(message + 'A1514ABA76583882').hexdigest().upper()
        message += sign
    message = '{:0>10}'.format(len(message)) + message
    message = message.decode('GBK')
    return message


def get_date_range(create_at_start, create_at_end):
    count = (datetime.datetime.strptime(str(create_at_end), "%Y-%m-%d") -
             datetime.datetime.strptime(str(create_at_start), "%Y-%m-%d")).days
    create_at_end_date = datetime.datetime.strptime(
        str(create_at_end), "%Y-%m-%d")
    return [datetime.datetime.strftime(create_at_end_date - datetime.timedelta(i), "%Y-%m-%d") for i in
            xrange(count + 1)]


def get_mon_seq(create_at_start, create_at_end):

    end_year, end_month = create_at_end.split('-')[:2]
    start_year, start_month = create_at_start.split('-')[:2]
    final = []
    if int(end_year) > int(start_year):
        s = [start_year + "-" + str('{:0>2}'.format(i))
             for i in range(int(start_month), 13)]
        e = [end_year + "-" + str('{:0>2}'.format(i))
             for i in range(1, int(end_month) + 1)]
        middle = [str(x) + "-" + str('{:0>2}'.format(j)) for x in range(int(start_year) + 1, int(end_year)) for j in
                  range(1, 13)]
        final = s + middle + e

    if int(end_year) == int(start_year):
        final = [start_year + "-" + str('{:0>2}'.format(i))
                 for i in range(int(start_month), int(end_month) + 1)]

    return final
# 修改和添加商户走api接口


@tornado.gen.coroutine
def create_or_update_merchant(METHOD, PATH, API_ID, APIKEY, multipart_data):
    date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    sign_body = '&'.join([METHOD, PATH, date, str(multipart_data.len), APIKEY])
    sign = md5(sign_body).hexdigest()

    headers = {
        'Authorization': 'Uline ' + API_ID + ':' + sign,
        'Date': date,
        'Content-Type': multipart_data.content_type,
    }

    ULINE_API_URL_PATH = ULINE_API_URL + PATH

    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(ULINE_API_URL_PATH, method=METHOD,
                                       headers=headers, body=multipart_data.to_string())
    raise tornado.gen.Return(json.loads(response.body))


def deal_data(data, offset):
    new_data = []
    for index, sigle_row in enumerate(data):
        new_row = list(sigle_row)
        new_row.insert(0, offset + index + 1)
        new_data.append(new_row)
    return new_data


@gen.coroutine
def deal_search_count_charts(index, date_range_key, search_count_details):

    date_range_default = defaultdict(int)
    for d in date_range_key:
        date_range_default[d] = 0

    day_tx_count = [(data[0], data[index])
                    for data in search_count_details]

    for k, v in day_tx_count:
        date_range_default[k] = round(date_range_default[k] + v, 2)

    raise gen.Return([[str(k), date_range_default[k]]
                      for k in sorted(date_range_default.keys())])


def common_date_deal(query_date, create_at_start, create_at_end):

    if int(query_date) == 1:
        # 模块下
        if create_at_end:
            create_at_end_search = parse_ymd(
                create_at_end) + datetime.timedelta(1)
        else:
            create_at_end = (
                datetime.datetime.now() - datetime.timedelta(1)).strftime("%Y-%m-%d")
            create_at_end_search = (
                datetime.datetime.now() + datetime.timedelta(1)).strftime("%Y-%m-%d")

        create_at_end = str(parse_ymd(
            create_at_end).strftime("%Y-%m-%d"))

        if create_at_start:
            create_at_start_search = parse_ymd(create_at_start) + \
                datetime.timedelta(1)
        else:
            create_at_start = (datetime.datetime.strptime(create_at_end, "%Y-%m-%d") - datetime.timedelta(days=6)).strftime(
                "%Y-%m-%d")
            create_at_start_search = (
                datetime.datetime.strptime(create_at_end, "%Y-%m-%d") - datetime.timedelta(days=5)).strftime(
                "%Y-%m-%d")

    if int(query_date) == 2:
        # 模块下
        if create_at_end:
            _year, _month = create_at_end.split('-')[:2]
        else:
            create_at_end = datetime.datetime.now().strftime('%Y-%m')
            _year, _month = create_at_end.split('-')
        if _month in [12, "12"]:
            _year = int(_year) + 1
            create_at_end_search = datetime.datetime(_year, 1, 1, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')
        else:
            create_at_end_search = datetime.datetime(int(_year), int(_month) + 1, 1, 23, 59, 59).strftime(
                '%Y-%m-%d %H:%M:%S')

        create_at_end = str(create_at_end)

        if create_at_start:
            _year, _month = create_at_start.split('-')[:2]
        else:
            now_date = datetime.datetime.now().strftime("%Y-%m-%d")
            create_at_start = (datetime.datetime.strptime(
                str(now_date), "%Y-%m-%d") - datetime.timedelta(days=150)).strftime('%Y-%m')
            _year, _month = create_at_start.split('-')
        create_at_start_search = datetime.datetime(int(_year), int(
            _month), 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
    return [create_at_start, create_at_end, create_at_start_search, create_at_end_search]


def query_common_date(query_date, create_at_start):

    if int(query_date) == 2:
        if not create_at_start:
            form_create_at_start = datetime.datetime.now().strftime('%Y-%m')
            _year, _month = form_create_at_start.split('-')
        else:
            form_create_at_start = create_at_start
            _year, _month = create_at_start.split('-')[:2]
        query_create_at_start = datetime.datetime(int(_year), int(
            _month), 2, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
        if _month in [12, "12"]:
            _year = int(_year) + 1
            query_create_at_end = datetime.datetime(_year, 1, 1, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')
        else:
            query_create_at_end = datetime.datetime(int(_year), int(_month) + 1, 1, 23, 59, 59).strftime(
                '%Y-%m-%d %H:%M:%S')

    if int(query_date) == 1:
        if not create_at_start:
            query_date_def = form_create_at_start = (timestamp_now().replace(
                hour=0, minute=0, second=0) - datetime.timedelta(days=1)).date()
        else:
            form_create_at_start = create_at_start
            query_date_def = parse_ymd(create_at_start)

        query_create_at_start = query_date_def + datetime.timedelta(days=1)
        query_create_at_end = query_date_def + datetime.timedelta(days=2)

    return [form_create_at_start, query_create_at_start, query_create_at_end]


def downloads_query_date(query_date, create_at_start, create_at_end):
    if int(query_date) == 1:
        # 模块下
        create_at_end_search = parse_ymd(
            create_at_end) + datetime.timedelta(1)
        create_at_start_search = parse_ymd(create_at_start) + \
            datetime.timedelta(1)
    else:
        # 模块下
        end_year, end_month = create_at_end.split('-')[:2]
        if end_month in [12, "12"]:
            _year = int(end_year) + 1
            create_at_end_search = datetime.datetime(_year, 1, 1, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')
        else:
            create_at_end_search = datetime.datetime(int(end_year), int(end_month) + 1, 1, 23, 59, 59).strftime(
                '%Y-%m-%d %H:%M:%S')
        s_year, s_month = create_at_start.split('-')[:2]
        create_at_start_search = datetime.datetime(int(s_year), int(
            s_month), 1, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
    return [create_at_start_search, create_at_end_search]


def gen_random_str(min_length=30, max_length=30, allowed_chars=(string.letters + string.digits)):
    if min_length == max_length:
        length = min_length
    else:
        length = choice(range(min_length, max_length))

    return ''.join([choice(allowed_chars) for i in range(length)])


def datetime_to_str(date_obj, format="%Y-%m-%d %H:%M:%S"):
    if not date_obj:
        return ''
    return date_obj.strftime(format)


def print_money(amount, precision=2, flag=""):
    format_str = "{{:{}.{}f}}".format(flag, precision)
    return format_str.format(amount)

