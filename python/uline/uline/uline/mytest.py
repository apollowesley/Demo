# -*- coding: utf-8 -*-
from tornado import gen, ioloop
from tornado.httpclient import AsyncHTTPClient
from uline.utils.wxpay.util import xml_to_dict
from uline.utils.wxpay.merchantInletToWxV2 import (
    MerchantInletToWx,
    UpdateMerchantInletToWx
)
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID,
    WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA
)
from uline.public.baseDB import DbClient
from uline.public import common

db = DbClient()

create_at = update_at = common.timestamp_now()


@gen.coroutine
def get_dt_inlet_info():
    query = """select
            dt_inlet_info.dt_name,
            dt_inlet_info.contact,
            dt_inlet_info.mobile,
            dt_inlet_info.email,
            dt_inlet_info.old_ind_code,
            dt_inlet_info.wx_ind_code,
            dt_inlet_info.dt_id,
            dt_inlet_info.service_phone
            from
            dt_inlet_info
            INNER JOIN dt_user on dt_user.dt_id=dt_inlet_info.dt_id
            where dt_user.wx_sub_mch_id is null and dt_user.status=2;"""
    ret = db.selectSQL(query, fetchone=False)
    raise gen.Return(ret)


@gen.coroutine
def create_wx_sub_dt_id(dt_inlet_info, APPID, WX_MCH_ID, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):

    wx_business_no = dt_inlet_info[
        5] if dt_inlet_info[5] else dt_inlet_info[4]
    mchInletToWx = MerchantInletToWx(
        APPID, WX_MCH_ID, WXPAY_KEY)
    shortName = u'招商银行微信支付商户'
    data = mchInletToWx.handle()(
        merchant_name=dt_inlet_info[0],
        merchant_shortname=shortName,
        service_phone=dt_inlet_info[7] if dt_inlet_info[7] else dt_inlet_info[2],
        contact=dt_inlet_info[1],
        contact_phone=dt_inlet_info[2],
        contact_email=dt_inlet_info[3],
        business=wx_business_no,
        merchant_remark=dt_inlet_info[6]
    )
    http_client = AsyncHTTPClient()
    response = yield http_client.fetch(
        "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=add",
        method='POST',
        body=data,
        client_key=WX_PRIVATE_KEY,
        client_cert=WX_PUB_KEY,
        ca_certs=WX_ROOT_CA
    )
    ret = xml_to_dict(response.body).get('root')
    if not ret:
        ret = dict(result_code='FAIL')
    print ret
    raise gen.Return(ret)


@gen.coroutine
def save_dt_inlet_to_wx(ret, dt_id):
    query = """
                insert into dt_inlet_to_wx_info (
                dt_id, return_code, return_msg,
                result_code, result_msg, create_at
                ) values (%s, %s, %s, %s, %s, %s);"""
    db.executeSQL(
        query,
        (
            dt_id,
            ret.get('result_code', 'FAIL'),
            ret.get('return_msg', 'FAIL'),
            ret.get('result_code', 'FAIL'),
            ret.get('result_msg', 'FAIL'),
            create_at
        )
    )


@gen.coroutine
def add_wx_sub_dt_id(wx_sub_dt_id, dt_id):
    query = """update dt_user set wx_sub_mch_id=%s,update_at=%s
    where dt_id=%s"""
    db.executeSQL(query, (wx_sub_dt_id, update_at, dt_id))


@gen.coroutine
def main():
    dt_inlet_info = yield get_dt_inlet_info()
    for _, data in enumerate(dt_inlet_info):
        dt_id = data[6]
        ret = yield create_wx_sub_dt_id(data, APPID, WX_MCH_ID, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        yield save_dt_inlet_to_wx(ret, dt_id)
        wx_sub_dt_id = ret.get('sub_mch_id')
        yield add_wx_sub_dt_id(wx_sub_dt_id, dt_id)

if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(main)
