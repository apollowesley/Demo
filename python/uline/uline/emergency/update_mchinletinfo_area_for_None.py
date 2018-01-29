#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import gen, ioloop
from uline.model.uline.info import MchInletInfo, AddressInfo
from uline.public.db import initdb, uline_session_scope
from uline.model.uline.base import uline_session
from uline.utils.alipay.get_areaname_by_upper_code import get_areanames_by_city


@gen.coroutine
def update_area_names():
    mchinletinfo_list = uline_session.query(
        MchInletInfo).filter(MchInletInfo.district == None, MchInletInfo.dt_id == '10000005554').all()
    print len(mchinletinfo_list)
    uline_session.close()
    for mchinletinfo in mchinletinfo_list:
        print mchinletinfo.district, mchinletinfo.city
        with uline_session_scope() as session:
            mchinletinfo.district = get_areanames_by_city(mchinletinfo.city)[0] if get_areanames_by_city(
                mchinletinfo.city) else None
            print mchinletinfo.district
            # session.add(mchinletinfo)


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(update_area_names)
