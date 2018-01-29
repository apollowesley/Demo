#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.options import define, options

from sqlalchemy.orm import aliased
from uline.public.db import initdb
from uline.public.db import uline_session_scope
from uline.model.uline.info import DtInletInfo, MchInletInfo
from uline.model.uline.user import MchUser, DtUser
from uline.utils.alipay import query_alipay
from uline.public import log
from uline.model.uline.info import MchBalance, DtBalance, MchPayment, DtPayment
from uline.utils.alipay.get_code_by_name import query_code_by_name
from uline.settings import MIN_ALI_LEVEL


define("dt_id", help="渠道商ID")
define("mch_ids", help="商户ID", default="")
define("chain_ids", help="连锁商户ID")


def update_dt_mch_alipid():
    dt_id = options.dt_id
    if not dt_id:
        return
    log.uline_script.info("----------start update dt ---------")
    alipay_pid = None
    valid_dt_id = True
    with uline_session_scope() as session:
        dt_info = session.query(DtInletInfo).filter(DtInletInfo.dt_id == dt_id).first()
        if dt_info:
            alipay_pid = dt_info.alipay_pid
        else:
            valid_dt_id = False
    if not valid_dt_id:
        raise Exception("没有对应的渠道商信息")

    if not alipay_pid:
        raise Exception("渠道商未填写对应的pid信息")

    # update_mch_pid(dt_id, alipay_pid)
    update_chain_pid(dt_id, alipay_pid)
    log.uline_script.info("----------------end update dt--------------\n\n\n")


def mch_has_ali_query(session):
    has_ali_query = session.query(MchPayment.mch_id).filter(MchPayment.uline_payment_code.like("ALI%"))
    has_ali_query = has_ali_query.filter(MchPayment.mch_id == MchInletInfo.mch_id)
    return has_ali_query.exsits()


def chain_has_ali_query(session):
    has_ali_query = session.query(DtPayment.dt_id).filter(DtPayment.uline_payment_code.like("ALI%"))
    has_ali_query = has_ali_query.filter(DtPayment.dt_id == MchUser.mch_id)
    return has_ali_query.exists()


def update_chains_pid():
    log.uline_script.info("---------start update chain-------")
    mch_ids = options.chain_ids
    mch_ids = mch_ids.split(',') if mch_ids else []
    fail_mchs = []
    invalid_mchs = []
    for mch_id in mch_ids:
        with uline_session_scope() as session:
            parent_info = aliased(DtInletInfo)
            mch_inlet_info_query = session.query(
                DtUser.ali_sub_mch_id,
                DtInletInfo.dt_id.label("merchant_id"),
                DtInletInfo.dt_name.label("merchant_name"),
                DtInletInfo.dt_short_name.label("merchant_shortname"),
                DtInletInfo.address,
                DtInletInfo.ali_ind_code,
                DtInletInfo.mobile,
                DtInletInfo.service_phone,
                DtInletInfo.email,
                DtInletInfo.head_mobile,
                DtInletInfo.head_name,
                DtInletInfo.province,
                DtInletInfo.city,
                DtInletInfo.district,
                DtInletInfo.license_type,
                DtInletInfo.license_num,
                DtBalance.id_card_no,
                DtBalance.balance_account,
                DtBalance.balance_name,
                parent_info.alipay_pid
            )
            mch_inlet_info_query = mch_inlet_info_query.join(DtInletInfo, DtInletInfo.dt_id == DtUser.dt_id)
            mch_inlet_info_query = mch_inlet_info_query.join(parent_info, parent_info.dt_id == DtInletInfo.parent_id)
            mch_inlet_info_query = mch_inlet_info_query.filter(DtInletInfo.dt_id == mch_id)
            mch_inlet_info_query = mch_inlet_info_query.filter(DtUser.ali_sub_mch_id != None)
            mch_inlet_info_query = mch_inlet_info_query.filter(DtUser.ali_sub_mch_id != '')
            # mch_inlet_info_query = mch_inlet_info_query.filter(chain_has_ali_query(session))
            mch_info = mch_inlet_info_query.first()
            mch_info = {key: getattr(mch_info, key, None) for key in mch_info.keys()} if mch_info else None
        if not mch_info:
            log.uline_script.info("无对应连锁商户:{}".format(mch_id))
            invalid_mchs.append(mch_id)
            continue
        if not mch_info['alipay_pid']:
            log.uline_script.info("渠道商没有支付宝pid")
            invalid_mchs.append(mch_id)
            continue
        is_success, msg = update_mch_ali_pid(mch_info, mch_info['alipay_pid'])
        if not is_success:
            fail_mchs.append(mch_id)
    log.uline_script.info(u"更新连锁商户pid失败有：{}".format(fail_mchs))
    log.uline_script.info(u"更新连锁商户pid无效的有：{}".format(invalid_mchs))
    log.uline_script.info("------end update chain pid------\n\n\n")


def update_mchs_pid():
    log.uline_script.info("---------start update mch-------")
    mch_ids = options.mch_ids
    mch_ids = mch_ids.split(',') if mch_ids else []
    fail_mchs = []
    invalid_mchs = []
    for mch_id in mch_ids:
        with uline_session_scope() as session:
            mch_inlet_info_query = session.query(
                MchUser.ali_sub_mch_id,
                MchInletInfo.mch_id.label("merchant_id"),
                MchInletInfo.mch_name.label("merchant_name"),
                MchInletInfo.mch_shortname.label("merchant_shortname"),
                MchInletInfo.ali_ind_code,
                MchInletInfo.mobile,
                MchInletInfo.service_phone,
                MchInletInfo.mch_id.label('merchant_id'),
                MchInletInfo.head_mobile,
                MchInletInfo.head_name,
                MchInletInfo.license_num,
                MchInletInfo.license_type,
                MchInletInfo.province,
                MchInletInfo.city,
                MchInletInfo.district,
                MchInletInfo.address,
                MchInletInfo.email,
                DtInletInfo.alipay_pid,
                MchBalance.balance_account,
                MchBalance.balance_name,
                MchBalance.id_card_no
            )
            mch_inlet_info_query = mch_inlet_info_query.join(MchInletInfo, MchInletInfo.mch_id == MchUser.mch_id)
            mch_inlet_info_query = mch_inlet_info_query.join(DtInletInfo, DtInletInfo.dt_id == MchInletInfo.dt_id)
            mch_inlet_info_query = mch_inlet_info_query.join(MchBalance, MchBalance.mch_id == MchUser.mch_id)
            mch_inlet_info_query = mch_inlet_info_query.filter(MchInletInfo.cs_id == None)
            mch_inlet_info_query = mch_inlet_info_query.filter(MchInletInfo.mch_id == mch_id)
            mch_inlet_info_query = mch_inlet_info_query.filter(MchUser.ali_sub_mch_id != None)
            mch_inlet_info_query = mch_inlet_info_query.filter(MchUser.ali_sub_mch_id != '')
            db_mch_info = mch_inlet_info_query.first()
            mch_info = {key: getattr(db_mch_info, key, None) for key in db_mch_info.keys()} if db_mch_info else None
        if not mch_info:
            log.uline_script.info("无对应商户:{}".format(mch_id))
            invalid_mchs.append(mch_id)
            continue
        if not mch_info['alipay_pid']:
            log.uline_script.info("渠道商没有支付宝pid")
            invalid_mchs.append(mch_id)
            continue
        print 'test'
        is_success, msg = update_mch_ali_pid(mch_info, mch_info['alipay_pid'])
        if not is_success:
            fail_mchs.append(mch_id)
    log.uline_script.info(u"更新普通商户pid失败有：{}".format(fail_mchs))
    log.uline_script.info(u"更新普通商户pid无效的有：{}".format(invalid_mchs))
    log.uline_script.info("------end update mch pid------\n\n\n")


def update_chain_pid(dt_id, alipay_pid):
    page = 0
    page_size = 1000
    has_data = True
    all_count = 0
    fail_mch_id = []
    success_count = 0
    while has_data:
        with uline_session_scope() as session:
            chain_user_info_query = session.query(
                DtUser.ali_sub_mch_id,
                DtInletInfo.dt_id.label("merchant_id"),
                DtInletInfo.dt_name.label("merchant_name"),
                DtInletInfo.dt_short_name.label("merchant_shortname"),
                DtInletInfo.address,
                DtInletInfo.ali_ind_code,
                DtInletInfo.mobile,
                DtInletInfo.service_phone,
                DtInletInfo.email,
                DtInletInfo.head_mobile,
                DtInletInfo.head_name,
                DtInletInfo.province,
                DtInletInfo.city,
                DtInletInfo.district,
                DtInletInfo.license_type,
                DtInletInfo.license_num,
                DtBalance.id_card_no,
                DtBalance.balance_account,
                DtBalance.balance_name
            )
            chain_user_info_query = chain_user_info_query.join(DtInletInfo, DtInletInfo.dt_id == DtUser.dt_id)
            chain_user_info_query = chain_user_info_query.filter(DtInletInfo.parent_id == dt_id)
            chain_user_info_query = chain_user_info_query.filter(DtUser.ali_sub_mch_id != None)
            chain_user_info_query = chain_user_info_query.filter(DtUser.ali_sub_mch_id != '')
            chain_user_info_query = chain_user_info_query.order_by(DtUser.create_at)
            chain_user_info_query = chain_user_info_query.offset(page * page_size)
            chain_user_info_query = chain_user_info_query.limit(page_size)
            mch_user_list = chain_user_info_query.all()
            mch_user_list = [{key: getattr(mch_user, key, '') for key in mch_user.keys()} for mch_user in mch_user_list]
        count = len(mch_user_list)
        if count:
            page = page + 1
        else:
            has_data = False
        for mch_user in mch_user_list:
            is_success, msg = update_mch_ali_pid(mch_user, alipay_pid)
            if not is_success:
                fail_mch_id.append(mch_user['merchant_id'])
            else:
                success_count += 1
        all_count += count
        if len(fail_mch_id) > 100:
            log.uline_script.info("超过100个连锁商户更新到支付宝失败")
            break
    log.uline_script.info("采集到的连锁商户总个数为:{}".format(all_count))
    log.uline_script.info("更新到支付宝失败的连锁商户个数为:{},id为:{}".format(len(fail_mch_id), fail_mch_id))
    log.uline_script.info("更新支付宝商户成功连锁商户个数为:{}".format(success_count))


def update_mch_pid(dt_id, alipay_pid):
    page = 0
    page_size = 1000
    has_data = True
    all_count = 0
    fail_mch_id = []
    success_count = 0
    while has_data:
        with uline_session_scope() as session:
            mch_user_info_query = session.query(
                MchUser.ali_sub_mch_id,
                MchInletInfo.mch_id.label("merchant_id"),
                MchInletInfo.mch_name.label("merchant_name"),
                MchInletInfo.mch_shortname.label("merchant_shortname"),
                MchInletInfo.address,
                MchInletInfo.ali_ind_code,
                MchInletInfo.mobile,
                MchInletInfo.service_phone,
                MchInletInfo.mch_id.label('merchant_id'),
                MchInletInfo.email,
                MchInletInfo.head_mobile,
                MchInletInfo.head_name,
                MchInletInfo.province,
                MchInletInfo.city,
                MchInletInfo.district,
                MchInletInfo.license_type,
                MchInletInfo.license_num,
                MchBalance.id_card_no,
                MchBalance.balance_account,
                MchBalance.balance_name
            )
            mch_user_info_query = mch_user_info_query.join(MchInletInfo, MchInletInfo.mch_id == MchUser.mch_id)
            mch_user_info_query = mch_user_info_query.join(MchBalance, MchBalance.mch_id == MchUser.mch_id)
            mch_user_info_query = mch_user_info_query.filter(MchInletInfo.dt_id == dt_id)
            mch_user_info_query = mch_user_info_query.filter(MchInletInfo.cs_id == None)
            mch_user_info_query = mch_user_info_query.filter(MchUser.ali_sub_mch_id != None)
            mch_user_info_query = mch_user_info_query.filter(MchUser.ali_sub_mch_id != '')
            mch_user_info_query = mch_user_info_query.order_by(MchUser.create_at)
            mch_user_info_query = mch_user_info_query.offset(page * page_size)
            mch_user_info_query = mch_user_info_query.limit(page_size)
            mch_user_list = mch_user_info_query.all()
            mch_user_list = [{key: getattr(mch_user, key, '') for key in mch_user.keys()} for mch_user in mch_user_list]
        count = len(mch_user_list)
        if count:
            page = page + 1
        else:
            has_data = False
        for mch_user in mch_user_list:
            is_success, msg = update_mch_ali_pid(mch_user, alipay_pid)
            if not is_success:
                fail_mch_id.append(mch_user['merchant_id'])
            else:
                success_count += 1
        all_count += count
        if len(fail_mch_id) > 100:
            log.uline_script.info("超过100个商户更新到支付宝失败")
            break
    log.uline_script.info("采集到的商户总个数为:{}".format(all_count))
    log.uline_script.info("更新到支付宝失败的商户个数为:{},id为:{}".format(len(fail_mch_id), fail_mch_id))
    log.uline_script.info("更新支付宝商户成功商户个数为:{}".format(success_count))


def update_mch_ali_pid(merchant_info, alipay_pid):
    query_dict = {
        'external_id': merchant_info['merchant_id'],
        'name': merchant_info['merchant_name'],
        'alias_name': merchant_info['merchant_shortname'],
        'service_phone': merchant_info['service_phone'] or merchant_info['mobile'],
        'source': alipay_pid,
        'category_id': merchant_info['ali_ind_code'],
    }
    level = 'M1'
    if merchant_info['district']:
        province_code, city_code, district_code = query_code_by_name(
            merchant_info['province'],
            merchant_info['city'],
            merchant_info['district'])

        # 如果有填区域信息，则以M2等级进件
        if province_code and city_code and district_code:
            query_dict['address_info'] = [{
                'province_code': province_code,
                'city_code': city_code,
                'district_code': district_code,
                'address': merchant_info['address'],
                'type': 'BUSINESS_ADDRESS'
            }]
            level = 'M2'

    if MIN_ALI_LEVEL.upper() >= "M3":
        m3_infos = {
            'business_license': merchant_info['license_num'],
            'business_license_type': merchant_info['license_type'],
            'contact_info': [{
                "name": merchant_info['head_name'],
                "type": 'OTHER',  # ;:法人，CONTROLLER:控制人, AGENT:代理人，OTHER：其他，
                "id_card_no": merchant_info['id_card_no'],
                "mobile": merchant_info['head_mobile'],
                # "phone": 座机,
                "email": merchant_info['email'],
            }],
            'bankcard_info': [{
                "card_no": merchant_info['balance_account'],
                "card_name": merchant_info['balance_name'],
            }],

        }
        query_dict.update(m3_infos)

    print(query_dict)
    # 如果有填区域信息，则以M2等级进件
    result = query_alipay.ali_api_block(query_dict, 'indirect_modify', level=level)
    ali_sub_mch_id = result.get('sub_merchant_id') if result.get('code') in ['10000', 10000] else ''
    is_success = bool(ali_sub_mch_id)
    msg_ali = result.get('sub_msg', '进件到支付宝发生未知错误,请联系客服!')
    if not is_success:
        log.uline_script.info(u"更新失败，merchant_id:{}, msg:{}".format(merchant_info['merchant_id'], msg_ali))
    return is_success, msg_ali


if __name__ == "__main__":
    options.parse_command_line()
    initdb()
    update_chains_pid()
    update_mchs_pid()
    update_dt_mch_alipid()
