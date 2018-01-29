#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv

from tornado import gen, ioloop
from uline.model.uline.info import IndustryUlineInfo, IndustryJDInfo
from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session


def address_info(filepath):
    """
    从京东提供的文件中提取新的行业信息
    """
    address_infos = []
    with open(filepath) as fp:
        reader = csv.reader(fp)
        next(reader, None)
        for row in reader:
            res = row[0].split('\t')
            address_infos.append([res[1], res[3], res[8], res[9]])
    return address_infos


def save_address(address_infos):
    for industry_code, status, jd_ind_code, industry_name in address_infos:
        industry_uline = uline_session.query(IndustryUlineInfo).\
            filter(IndustryUlineInfo.industry_code == industry_code).first()
        industry_uline.status = status
        industry_uline.jd_ind_code = jd_ind_code
        uline_session.commit()

        industry_jd = uline_session.query(IndustryJDInfo).\
            filter(IndustryJDInfo.industry_code == jd_ind_code).first()
        if industry_jd is None and status != '2':
            with uline_session_scope() as session:
                industry_jd = IndustryJDInfo()
                industry_jd.industry_code = jd_ind_code
                industry_jd.industry_name = industry_name
                # industry_alipay.industry_name = industry_name.decode('gbk')
                industry_jd.status = status
                session.add(industry_jd)


@gen.coroutine
def main():
    # filepath = '../doc/ULINE经营类目针对支付宝进件接口迭代.txt'
    filepath = '/Users/apple/ulaiber-projects/uline/doc/ULINE经营类目针对京东进件接口迭代.txt'
    address_infos = address_info(filepath)
    save_address(address_infos)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)