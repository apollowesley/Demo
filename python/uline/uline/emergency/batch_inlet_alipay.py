#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict

from tornado import gen, ioloop
from uline.model.uline.base import uline_session
from uline.model.uline.info import MchInletInfo, AddressInfo
from uline.model.uline.user import MchUser
from uline.public.db import initdb
from sqlalchemy import or_
from uline.utils.alipay.get_code_by_name import query_code_by_name
from uline.utils.alipay.query_alipay import query_alipay_mch_common, update_alipay_mch_common
import copy
from uline.public import log


def query_mch_info(mch_id):
    return uline_session.\
        query(MchInletInfo.province, MchInletInfo.city, MchInletInfo.district,
              MchInletInfo.address, MchInletInfo.ali_ind_code).\
        filter(MchInletInfo.mch_id == mch_id, MchInletInfo.district.isnot(None)).first()


def query_all_ali_mch():
    return uline_session.query(MchUser.mch_id, MchInletInfo.district).\
        join(MchInletInfo, MchInletInfo.mch_id == MchUser.mch_id).\
        filter(MchUser.ali_sub_mch_id.isnot(None),
               MchUser.ali_level.is_(None),
               MchInletInfo.district.isnot(None)).all()


# def query_code_by_name(province, city, district):
#     try:
#         province_code = uline_session.query(AddressInfo.area_code).\
#             filter(or_(AddressInfo.short_name == province,
#                        AddressInfo.area_name == province)).first()
#
#         city_code = uline_session.query(AddressInfo.area_code).\
#             filter(AddressInfo.area_name == city,
#                    AddressInfo.upper_code == province_code[0]).first()
#
#         district_code = uline_session.query(AddressInfo.area_code).\
#             filter(AddressInfo.area_name == district,
#                    AddressInfo.upper_code == city_code[0]).first()
#     except:
#         return None, None, None
#
#     return province_code[0], city_code[0], district_code[0]


@gen.coroutine
def mch_indirect_query(mch_id):
    query_dict = {'external_id': mch_id}
    ali_ret = yield query_alipay_mch_common(query_dict)
    raise gen.Return(ali_ret)


@gen.coroutine
def mch_indirect_update(query_dict):
    ali_ret = yield update_alipay_mch_common(query_dict)
    raise gen.Return(ali_ret)


@gen.coroutine
def main():
    """
    获取有支付宝支付的商户
    """

    # 查询支付宝商户的等级
    # mch_ids = ['100000168880']
    # 获取所有拥有 ali_sub_mch_id 的商户id
    mch_ids = query_all_ali_mch()

    address_error = []
    update_success = []
    update_error = []
    has_address = []
    not_level = []

    for mch_id, district in mch_ids:

        res = yield mch_indirect_query(mch_id)

        # 将M1商户升级为M2
        if res.get('code') == '10000':
            if not res.get('indirect_level'):
                not_level.append(mch_id)
            # 如果是M2,则保存到数据库
            if res.get('indirect_level') and res.get('indirect_level').endswith('M2'):
                mch_user = uline_session.query(MchUser).\
                    filter(MchUser.mch_id == mch_id).first()
                if mch_user.ali_level != 'M2':
                    mch_user.ali_level = 'M2'
                    uline_session.commit()
                continue
            # todo 处理支付宝返回信息中没有indirect_level值的商户
            if res.get('indirect_level') and res.get('indirect_level').endswith('M1'):
                mch_user = uline_session.query(MchUser).\
                    filter(MchUser.mch_id == mch_id).first()
                if mch_user.ali_level != 'M1':
                    mch_user.ali_level = 'M1'
                    uline_session.commit()
                # 如果已经有address信息
                if res.get('address'):
                    has_address.append(mch_id)
                    continue
                query_dict = copy.deepcopy(res)
                query_dict.pop('code')
                query_dict.pop('indirect_level')
                query_dict.pop('msg')

                # 获取商户新的行业类别和地址信息
                temp = query_mch_info(mch_id)
                if not temp:
                    address_error.append(mch_id)
                    continue
                mch_info = list(query_mch_info(mch_id))
                # 转换地址信息
                query_dict['category_id'] = mch_info.pop()
                address = mch_info.pop()
                try:
                    province_code, city_code, district_code = query_code_by_name(*mch_info)
                except:
                    province_code = city_code = district_code = None
                    address_error.append(mch_id)
                # 地址信息存在错误
                if not (province_code or city_code or district_code):
                    address_error.append(mch_id)
                    continue
                query_dict['address_info'] = [{
                    'province_code': province_code,
                    'city_code': city_code,
                    'district_code': district_code,
                    'address': address,
                    'type': 'BUSINESS_ADDRESS'
                }]

                # query_dict['category_id'] = '2015050700000000'
                # query_dict['address_info'] = [{
                #     'province_code': '440000',
                #     'city_code': '440300',
                #     'district_code': '440305',
                #     'address': '科技园麻雀岭工业区M-10栋',
                #     'type': 'BUSINESS_ADDRESS'
                # }]

                res_update = yield mch_indirect_update(query_dict)
                if res_update.get('code') != '10000':
                    update_error.append(mch_id)
                else:
                    update_success.append(mch_id)

    log.uline_script.info(u'address_error:%s' % address_error)
    log.uline_script.info(u'update_error:%s' % update_error)
    log.uline_script.info(u'update_success:%s' % update_success)
    log.uline_script.info(u'has_address:%s' % has_address)
    log.uline_script.info(u'not_level:%s' % not_level)


if __name__ == '__main__':
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
