#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import csv

from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo
from uline.public.db import initdb
from uline.model.uline.base import uline_session


def address_info(filepath):
    # 处理下xlsx文件，用number打开xlsx文件，复制数据到新建的csv文件中
    # 渠道商名称，渠道商编号，商户名称，商户编号，省，市， 区，地址
    address_infos = []
    with open(filepath) as fp:
        reader = csv.reader(fp)
        next(reader, None)
        for row in reader:
            # row = row[0].split('\t')
            if len(row) >= 8:
                address_infos.append([row[3], row[4].decode('gbk'), row[5].decode('gbk'),
                                      row[6].decode('gbk'), row[7].decode('gbk')])
    return address_infos


def save_address(address_infos):
    for mch_id, province, city, district, address in address_infos:
        mch_inlet_info = uline_session.query(MchInletInfo).\
            filter(MchInletInfo.mch_id == mch_id).first()
        print mch_id
        if mch_inlet_info.province != province:
            print mch_inlet_info.province, province
            mch_inlet_info.province = province

        if mch_inlet_info.city != city:
            print mch_inlet_info.city, city
            mch_inlet_info.city = city

        if mch_inlet_info.district != district:
            print mch_inlet_info.district, district
            mch_inlet_info.district = district

        if mch_inlet_info.address != address:
            print mch_inlet_info.address, address
            mch_inlet_info.address = address

        # uline_session.commit()


@gen.coroutine
def main():
    # filepath = '/Users/apple/ulaiber-projects/uline/doc/cmbc.csv'
    filepath = '/Users/apple/ulaiber-projects/uline/doc/5.txt'
    address_infos = address_info(filepath)
    save_address(address_infos)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
