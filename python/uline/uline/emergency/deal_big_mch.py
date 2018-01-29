#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import pprint
import json
from collections import defaultdict
import csv
import argparse

from tornado import gen, ioloop
from uline.utils.wxpay import query_wx
from uline.settings import (
    WX_MCH_ID, WXPAY_KEY, APPID, WX_PUB_KEY, WX_PRIVATE_KEY, WX_ROOT_CA,
    WX_APP_MCH_ID, WXPAY_APP_KEY, WX_APP_APPID, WX_APP_PUB_KEY,
    WX_APP_PRIVATE_KEY, WX_APP_ROOT_CA,
)
from uline.public.db import initdb
from uline.model.uline.base import uline_session
from uline.model.uline.base import MchInletInfo, MchUser, DtUser, DtInletInfo
from uline.public import log


def nested_dict(): return defaultdict(nested_dict)


MCH_RESULT = nested_dict()


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


my_pprint = MyPrettyPrinter().pprint


@gen.coroutine
def get_wx_mch_info(sub_mch_id, mch_type):

    mch_type_name = u'公众号' if mch_type == 'wx' else u'微信app'
    args = {'sub_mch_id': sub_mch_id}

    log.uline_script.info(u'获取微信%s商户%s信息' % (mch_type_name, sub_mch_id))
    if mch_type == 'wx':
        args['appid'] = APPID
        args['mch_id'] = WX_MCH_ID
        result = yield query_wx.get_wx_mch_info(args, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
    else:
        args['appid'] = WX_APP_APPID
        args['mch_id'] = WX_APP_MCH_ID
        result = yield query_wx.get_wx_mch_info(args, WXPAY_APP_KEY, WX_APP_PRIVATE_KEY,
                                                WX_APP_PUB_KEY, WX_APP_ROOT_CA)

    wx_mch_info = None
    if result and 'mchinfo' in result:
        mch_infos = result['mchinfo']
        if isinstance(mch_infos, dict):
            mch_infos = [mch_infos]
        for mch_info in mch_infos:
            if mch_info['mch_id'] == sub_mch_id:
                wx_mch_info = mch_info

    raise gen.Return(wx_mch_info)


@gen.coroutine
def add_wx_mch(mch_info, mch_type):
    """
    进件商户到微信
    """
    mch_type_name = u'公众号' if mch_type == 'wx' else u'微信app'
    log.uline_script.info(u'进件商户%s到微信%s' %
                          (mch_info['merchant_remark'], mch_type_name))
    result = yield query_wx.create_wx_mch(mch_info, mch_info.pop('wx_pay_key'),
                                          mch_info.pop('wx_private_key'),
                                          mch_info.pop('wx_pub_key'),
                                          mch_info.pop('wx_root_ca'))
    sub_mch_id = None
    if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
        sub_mch_id = result['sub_mch_id']
        MCH_RESULT[mch_info['merchant_remark']]['add_result'] = 'success'
        log.uline_script.info(u'进件到商户%s到微信%s成功' % (mch_info['merchant_remark'], mch_type_name))
    else:
        error_msg = result.get('result_msg', '进件到微信支付出现未知错误!请联系客服!')
        if isinstance(error_msg, str):
            error_msg = error_msg.decode('utf-8')
        log.uline_script.info(u'进件到商户%s到微信%s失败: %s' % (mch_info['merchant_remark'], mch_type_name, error_msg))
        MCH_RESULT[mch_info['merchant_remark']]['add_result'] = 'fail'
        MCH_RESULT[mch_info['merchant_remark']]['reason'] = error_msg
    MCH_RESULT[mch_info['merchant_remark']]['mch_type'] = mch_type
    raise gen.Return(sub_mch_id)


@gen.coroutine
def add_new_config(sub_mch_id, mch_type, ul_mch_id, dt_info):
    """
    修改商户配置
    """
    config_infos = []
    info = {
        'sub_mch_id': sub_mch_id
    }

    if mch_type == 'wx':
        info['mch_id'] = WX_MCH_ID
        info['appid'] = APPID
    elif mch_type == 'wx_app':
        info['mch_id'] = WX_APP_MCH_ID
        info['appid'] = WX_APP_APPID
    else:
        raise ValueError(u'不支持的商户进件类型')

    if dt_info.get('jsapi_path'):
        jsapi_path_list = dt_info.get('jsapi_path')
        for jsapi_path in jsapi_path_list:
            log.uline_script.info(u'修改商户%s授权目录配置: %s' % (ul_mch_id, jsapi_path))
            config_infos.append(dict(info, **{'jsapi_path': jsapi_path,
                                              'config_type': 'jsapi_path'}))

    subscribe_appid_list  = dt_info.get('subscribe_appid')
    if subscribe_appid_list:
        for subscribe_appid in subscribe_appid_list:
            log.uline_script.info(u'修改商户%s推荐关注appid: %s' % (ul_mch_id, subscribe_appid))
            config_infos.append(dict(info, **{'subscribe_appid': subscribe_appid,
                                              'config_type': 'subscribe_appid'}))

    sub_appid_list = dt_info.get('sub_appid')
    if sub_appid_list:
        for sub_appid in sub_appid_list:
            log.uline_script.info(u'修改商户%s关联appid: %s' % (ul_mch_id, sub_appid))
            config_infos.append(dict(info, **{'sub_appid': sub_appid,
                                              'config_type': 'sub_appid'}))


    for config_info in config_infos:
        config_type = config_info.pop('config_type')
        if mch_type == 'wx':
            result = yield query_wx.add_mch_appid(config_info, WXPAY_KEY, WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA)
        else:
            result = yield query_wx.add_mch_appid(config_info, WXPAY_APP_KEY, WX_APP_PRIVATE_KEY,
                                                  WX_APP_PUB_KEY, WX_APP_ROOT_CA)

        # 将结果记录起来
        if result['return_code'] == 'SUCCESS' and result['result_code'] == 'SUCCESS':
            MCH_RESULT[ul_mch_id][config_type][config_info[config_type]]['change_result'] = 'success'
            log.uline_script.info(u'%s配置%s成功' % (ul_mch_id, config_info[config_type]))
        else:
            error_msg = result.get('err_code_des', '修改子商户配置出现位置错误!')
            if isinstance(error_msg, str):
                error_msg = error_msg.decode('utf-8')
            log.uline_script.info(u'%s配置%s失败， %s' % (ul_mch_id, config_info[config_type], error_msg))
            MCH_RESULT[ul_mch_id][sub_mch_id][config_type][config_info[config_type]]['reason'] = error_msg
            MCH_RESULT[ul_mch_id][sub_mch_id][config_type][config_info[config_type]]['change_result'] = 'fail'
        MCH_RESULT[ul_mch_id][sub_mch_id]['mch_type'] = mch_type

@gen.coroutine
def get_all_mch_infos(dt_id, mch_id=None, force=False):
    """
    获取该渠道商下面所有大商户, 并返回商户信息，方便后面进件到微信，添加微信商户配置
    :param dt_id: 渠道商id
    :return: 所有需要进件到微信那边的商户信息
    """
    mch_users = []
    db_dt_user = uline_session.query(DtUser).filter(DtUser.dt_id == dt_id).first()
    db_dt_inlet_info = uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == dt_id).first()

    if not db_dt_user:
        return

    db_mch_infos = uline_session.query(MchInletInfo, MchUser) \
        .filter(MchInletInfo.mch_id == MchUser.mch_id) \
        .filter(MchInletInfo.dt_id == dt_id) \
        .filter(MchUser.wx_use_parent == 2)

    if mch_id:
        db_mch_infos = db_mch_infos.filter(MchUser.mch_id == mch_id)
    db_mch_infos = db_mch_infos.all()

    for mch_inlet_info, mch_user in db_mch_infos:

        if mch_user.wx_use_parent != 2:
            continue

        # 是否需要进件微信公众号商户
        wx_should_add = False
        if mch_user.wx_sub_mch_id:
            if force:
                wx_should_add = True
            else:
                wx_mch_info = yield get_wx_mch_info(mch_user.wx_sub_mch_id, 'wx')
                if wx_mch_info and wx_mch_info['merchant_name'] != mch_inlet_info.mch_name:
                    wx_should_add = True

        # # 是否需要进件微信app商户
        # wx_app_should_add = False
        # if mch_user.wx_app_sub_mch_id:
        #     wx_mch_info = yield get_wx_mch_info(mch_user.wx_app_sub_mch_id, 'wx_app')
        #     if force or (wx_mch_info and wx_mch_info['merchant_name'] != mch_inlet_info.mch_name):
        #         wx_app_should_add = True

        # if not (wx_should_add or wx_app_should_add):
        if not wx_should_add:
            log.uline_script.info(u"商户%s:%s不需要进件到微信" % (mch_user.mch_id, mch_user.mch_name))
            continue

        mch_user = {
            "merchant_name": mch_inlet_info.mch_name,
            "merchant_shortname": mch_inlet_info.mch_shortname,
            "service_phone": mch_inlet_info.service_phone,
            'contact': mch_inlet_info.contact,
            "contact_phone": mch_inlet_info.mobile,
            "contact_email": mch_inlet_info.email,
            "business": mch_inlet_info.wx_ind_code,
            "merchant_remark": mch_user.mch_id,
        }

        if wx_should_add:
            wx_mch_info = {
                "appid": APPID,
                "mch_id": WX_MCH_ID,
                "wx_pay_key": WXPAY_KEY,
                "wx_private_key": WX_PRIVATE_KEY,
                "wx_pub_key": WX_PUB_KEY,
                "wx_root_ca": WX_ROOT_CA,
                "mch_type": 'wx',
            }
            if db_dt_inlet_info.wx_channel_id:
                wx_mch_info['channel_id'] = db_dt_inlet_info.wx_channel_id
            mch_users.append(
                dict(mch_user, **wx_mch_info)
            )
        # if wx_app_should_add:
        #     wx_app_mch_info = {
        #         "appid": WX_APP_APPID,
        #         "mch_id": WX_APP_MCH_ID,
        #         "wx_pay_key": WXPAY_APP_KEY,
        #         "wx_private_key": WX_APP_PRIVATE_KEY,
        #         "wx_pub_key": WX_APP_PUB_KEY,
        #         "wx_root_ca": WX_APP_ROOT_CA,
        #         "mch_type": 'wx_app',
        #     }
        #     if db_dt_inlet_info.wx_app_channel_id:
        #         wx_app_mch_info['channel_id'] = db_dt_inlet_info.wx_app_channel_id
        #     mch_users.append(
        #         dict(mch_user,  **wx_app_mch_info)
        #     )
    raise gen.Return(mch_users)


def get_dt_infos(filepath):
    """
    从用户提供的配置文件中提取渠道商相关信息
    """
    dt_infos = []
    with open(filepath) as fp:
        reader = csv.reader(fp)
        next(reader, None)
        for row in reader:
            dt_info = {
                'dt_id': row[0],
                'subscribe_appid': len(row) > 2 and row[2].replace('\n', ' ').rstrip().split(),
                'jsapi_path': len(row) > 3 and row[3].replace('\n', ' ').split(),
                'sub_appid': len(row) > 4 and row[4].split(),
            }
            dt_infos.append(dt_info)
    return dt_infos

def get_args():
    parser = argparse.ArgumentParser(description=u"更新渠道下面大商户信息")
    parser.add_argument("file_path",help=u"渠道商信息文件")
    parser.add_argument("-m", "--mch_id", help=u"商户号")
    parser.add_argument("-f", "--force", help=u"重新修改所有大商户", action="store_true")
    args = parser.parse_args()
    return args


@gen.coroutine
def main():
    # 处理命令行参数
    args = get_args()

    filepath = args.file_path
    log.uline_script.info(u'开始批量修改存量大商户信息')
    # 从文件中获取渠道商信息
    dt_infos = get_dt_infos(filepath)
    print(dt_infos)
    for dt_info in dt_infos:
        log.uline_script.info(u'修改渠道商%s下面商户信息' % dt_info['dt_id'])
        mch_infos = yield get_all_mch_infos(dt_id=dt_info['dt_id'], mch_id=args.mch_id, force=args.force)
        if not mch_infos:
            continue
        for mch_info in mch_infos:
            mch_type = mch_info.pop('mch_type')
            # 进件商户到微信那边
            sub_mch_id = yield add_wx_mch(mch_info, mch_type)
            if sub_mch_id:
                # 修改商户配置
                yield add_new_config(sub_mch_id,
                                     mch_type,
                                     mch_info['merchant_remark'],
                                     dt_info)
            else:
                log.uline_script.error(u"进件商户%s到微信出错" % mch_info['merchant_remark'])
                continue

            time.sleep(0.2)
            # 更新数据库中存储的微信商户号
            mch_user = uline_session.query(MchUser). \
                filter(MchUser.mch_id == mch_info['merchant_remark'])
            if mch_type == "wx":
                mch_user.update({"wx_sub_mch_id": sub_mch_id})
            elif mch_type == "wx_app":
                mch_user.update({"wx_app_sub_mch_id": sub_mch_id})
            else:
                raise ValueError('Unknown wx_type')
            uline_session.commit()

    my_pprint(json.loads(json.dumps(MCH_RESULT)))


if __name__ == "__main__":
    initdb()
    ioloop.IOLoop.instance().run_sync(main)
