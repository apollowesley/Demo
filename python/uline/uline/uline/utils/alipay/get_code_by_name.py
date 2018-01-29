#!/usr/bin/env python
# -*- coding: utf-8 -*-
from uline.model.uline.base import uline_session
from uline.model.uline.info import AddressInfo
from uline.public.db import initdb
from sqlalchemy import or_
from uline.utils.alipay.get_areaname_by_upper_code import get_areanames_by_city

initdb()


def query_code_by_name(province, city, district):
    try:
        # 特殊处理 province 为 北京市、上海市、重庆市、天津市
        if province in [u'北京市', u'上海市', u'重庆市', u'天津市']:
            province = province[:-1]

        if province == u'港澳台':
            province_code = '1'

        else:
            province_code = uline_session.query(AddressInfo.area_code).\
                filter(or_(AddressInfo.short_name == province,
                           AddressInfo.area_name == province)).first()

        city_code = uline_session.query(AddressInfo.area_code).\
            filter(or_(AddressInfo.area_name == city,
                       AddressInfo.short_name == city,), AddressInfo.upper_code == province_code[0]).first()

        district_code = uline_session.query(AddressInfo.area_code).\
            filter(AddressInfo.area_name == district,
                   AddressInfo.upper_code == city_code[0]).first()

        if not district_code:
            district = (get_areanames_by_city(city))[0]
            district_code = uline_session.query(AddressInfo.area_code).\
                filter(AddressInfo.area_name == district,
                       AddressInfo.upper_code == city_code[0]).first()
    except:
        return None, None, None

    if province_code and city_code and district_code:
        return province_code[0], city_code[0], district_code[0]
    else:
        return None, None, None
