#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from tornado import gen, ioloop
from uline.model.uline.info import AddressInfo
from uline.public.db import initdb, uline_session_scope


def address_info(filepath):
    """
    从支付宝提供的文件中提取地区信息
    """
    address_infos = []
    with open(filepath) as fp:
        reader = csv.reader(fp)
        next(reader, None)
        for row in reader:
            address_infos.append([row[0], row[1], row[2], row[3]])
    return address_infos


def save_address(address_infos):
    for short_name, area_code, area_name, upper_code in address_infos:
        with uline_session_scope() as session:
            address = AddressInfo()
            address.short_name = short_name.decode('gbk')
            address.area_code = area_code
            address.area_name = area_name.decode('gbk')
            address.upper_code = upper_code
            session.add(address)


@gen.coroutine
def main():
    # filepath = '../doc/地区码_20170531.csv'
    filepath = '/Users/apple/ulaiber-projects/uline/doc/地区码_20170531.csv'
    address_infos = address_info(filepath)
    save_address(address_infos)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
