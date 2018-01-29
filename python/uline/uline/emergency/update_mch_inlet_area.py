#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo, AddressInfo
from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.utils.alipay.get_areaname_by_upper_code import get_areanames_by_city
from sqlalchemy import text


@gen.coroutine
def update_area_names():
    # 100000034919   北塘区 |成都市  双流县
    addressinfos = uline_session.query(AddressInfo.area_name).all()
    addressinfo_list = [addressinfo[0] for addressinfo in addressinfos]
    mchinletinfo_list = uline_session.query(MchInletInfo).filter(
        text('district ~ :reg')).params(reg='[\u4e00-\u9fa5]+').all()
    uline_session.close()
    print len(mchinletinfo_list)
    need_deal = []
    for mchinletinfo in mchinletinfo_list:
        if mchinletinfo.district not in addressinfo_list:
            district_str = mchinletinfo.district[:-1]
            print mchinletinfo.district, mchinletinfo.city
            areaname_compare = get_areanames_by_city(mchinletinfo.city)
            areaname_list = [
                areaname for areaname in areaname_compare if areaname.startswith(district_str)]
            if not areaname_list:
                with uline_session_scope() as session:
                    district = mchinletinfo.district
                    mchinletinfo.district = areaname_compare[0]
                    need_deal.append(
                        dict(mch_id=mchinletinfo.mch_id, district=district, city=mchinletinfo.city,
                             areaname=mchinletinfo.district))
                    session.add(mchinletinfo)
            if areaname_list.__len__() == 1:
                print areaname_list[0]
                with uline_session_scope() as session:
                    district = mchinletinfo.district
                    mchinletinfo.district = areaname_list[0]
                    need_deal.append(
                        dict(mch_id=mchinletinfo.mch_id, district=district, city=mchinletinfo.city,
                             areaname=mchinletinfo.district))
                    session.add(mchinletinfo)

    print need_deal


if __name__ == "__main__":
    # print a.__len__()
    # print a[:-3]

    initdb()
    ioloop.IOLoop.instance().run_sync(update_area_names)
