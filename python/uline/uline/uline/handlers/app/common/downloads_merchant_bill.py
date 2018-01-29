#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline.handlers.baseHandlers import CommanHandler
from tornado.web import authenticated, asynchronous
from tornado import gen
from os import path
from datetime import datetime
from tornado.concurrent import run_on_executor
from .form import DownloadsBill
from uline.public import common
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
import tcelery
from uline.backend.common.generate_merchant_bills import generate_zip
from uline.public.constants import DOWNLOAD_FILE_NUM_LIMIT
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()
thread_num = cpu_count()
cur_dir = path.dirname(path.dirname(
    path.dirname(path.dirname(path.abspath(__file__)))))


class DownloadsMerchantBill(CommanHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = DownloadsBill(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg="请重新输入参数")
            self.finish(f_rsp)
            return
        self.charac_id = int(self.form.charac_id.data)

    # @authenticated
    def get(self):
        link_str = {"1": 'bank', "5": 'official',
                    "2": 'distributor', "3": 'chain', "4": 'merchant'}
        str_link = link_str[str(self.charac_id)] + \
            "/reconciliation/downloads.html"

        if self.charac_id in [1, 5]:
            self.render(str_link)
            return

        if self.charac_id == 4:
            self.render(str_link, id=self.get_user()[str(self.charac_id)])
            return

        name = self.db.selectSQL(
            "select dt_name from dt_inlet_info where dt_id = %s;",
                                (self.get_user()[str(self.charac_id)],))

        if self.charac_id in [2, 3]:
            self.render(str_link, id=self.get_user()[str(
                self.charac_id)], name=name[0])
            return

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def post(self):
        self.create_at_start = self.form.create_at_start.data
        if datetime.strptime(str(self.create_at_start), "%Y-%m-%d") < datetime.strptime('2016-01-01', "%Y-%m-%d"):
            f_rsp = common.f_rsp(code=406, msg="起始日期请输入2016年1月1日以后的日期")
            self.finish(f_rsp)
            return
        self.create_at_end = self.form.create_at_end.data
        yield self.async_generate_zip()

    def query_mch_id(self):
        self.id = self.form.id.data
        self.query_charac = int(self.form.query_charac.data)
        # 如果查询的是渠道商或者连锁商户
        if len(self.id) == 11:
            query = "select mch_id from mch_inlet_info where dt_id = %s;" if self.query_charac == 1\
                else "select mch_id from mch_inlet_info where cs_id = %s;"
            ret = self.db.selectSQL(query, (self.id,), fetchone=False)
            mch_ids = [i[0] for i in ret]
        else:
            mch_ids = [self.id, ]

        return mch_ids

    @gen.coroutine
    def async_generate_zip(self):
        mch_ids = self.query_mch_id()
        if not mch_ids:
            data = {"code": 406, "msg": "未查到任何商户"}
            self.write(data)
            return
        ret = yield self.generate_zip(mch_ids)
        if ret.get('static_path'):
            data = {"code": 200, "msg": "下载成功",
                    "data": ret.get('static_path')}
        elif ret.get('order'):
            data = {"code": 201, "msg": "已经预约下载"}
        elif ret.get('over_order'):
            data = {"code": 202, "msg": "下载任务已经超过50条，请删除不需要的任务"}
        else:
            data = {"code": 406, "msg": ret.get("msg", "fail")}
        self.finish(data)
        return

    @gen.coroutine
    def generate_zip(self, mch_ids):

        date_range = sorted(common.get_date_range(
            self.create_at_start, self.create_at_end))
        # 获取打包文件的地址, 获取打包文件后的目录,包含年月日
        all_day_csv, all_day_zip = self.get_dir(date_range, mch_ids)
        all_csv = filter(lambda x: path.isfile(
            x[0]), zip(all_day_csv, all_day_zip))
        charac = {"1": "渠道商", "2": "商户", "3": "门店"}
        message = '此{}在指定日期未生成账单'.format(charac[str(self.query_charac)])
        if not all_csv:
            data = {"code": 406, "msg": message}
            raise gen.Return(data)

        num_csvs = len(all_csv)
        # 如果下载文件只有一个,则直接下载,如果下载文件多于一个,则预约下载
        if num_csvs == 1:
            response = yield gen.Task(generate_zip.apply_async,
                                      args=[self.get_user()[str(self.charac_id)], all_csv, num_csvs])
            ret = response.result
        else:

            d_num = yield self.get_download_num()
            if d_num < DOWNLOAD_FILE_NUM_LIMIT:
                generate_zip.delay(self.get_user()[str(self.charac_id)], all_csv, num_csvs)
                ret = {'order': True}
            else:
                ret = {'over_order': True}

        raise gen.Return(ret)

    @gen.coroutine
    def get_download_num(self):
        query = """select count(1) from order_download_info where user_id=%s and status in (1,2,3,4);"""
        ret = self.db.selectSQL(query, (self.get_user()[str(self.charac_id)],))
        raise gen.Return(ret[0])

    def get_dir(self, date_range, mch_ids):
        # 挂载在static/merchant_bill里面
        user_dl_path = path.join(cur_dir, "static/merchant_bill")
        all_day_zip, all_day_date_zip = [], []
        for mch in mch_ids:
            for data in date_range:
                data = list(map(int, data.split('-')))
                data.append(mch)
                day_file_mch = path.join(user_dl_path, '{}/{}/{}/{}.csv'.format(*data))
                day_file_mch_date = path.join("", "{}年/{}月/{}日/{}.csv".format(*data))
                all_day_zip.append(day_file_mch)
                all_day_date_zip.append(day_file_mch_date)
        return [all_day_zip, all_day_date_zip]
