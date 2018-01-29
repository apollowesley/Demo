#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from tornado import gen, ioloop
from datetime import datetime, timedelta
from uline.public.common import gen_randown_mch_pkey
import time


def get_dt_id():
    """从命令行获取渠道商id"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dt_id', metavar='DT_ID', type=str,
                        help='input mch_id')
    args = parser.parse_args()
    return args.dt_id


# import uline.backend.bank.automatic_review_activate as auto_review
import uline.backend.bank.automatic_review_activate_for_d0 as auto_review


@gen.coroutine
def main():
    dt_id = get_dt_id()
    # dt_id = '10000000830'
    # dt_ids = [10000005554, 10000006774, 10000063337, 10000050727, 10000037107, 10000045429, 10000056667,
    #           10000101520, 10000086344]
    # for dt_id in dt_ids:
    # dt_ids = [10000000830]
    # 开始批量审核d0商户时间
    begin_time = datetime.now()
    all_auth_mch_ids = []
    # for dt_id in dt_ids:
    if dt_id:
        mch_ids = set(auto_review.get_dt_un_auth_d0_mch(dt_id))
        print mch_ids
        if mch_ids:
            mch_ids = [str(mch_id) for mch_id in mch_ids]
            flag = yield auto_review.automatic_review(mch_ids)
            # 如果审核成功
            if flag:
                all_auth_mch_ids.extend(mch_ids)

    # 如果有审核通过，未激活的商户
    if all_auth_mch_ids:
        # 批量审核结束时间
        end_time = datetime.now()
        # 判断时间是否超过10分钟
        diff = timedelta(minutes=12).seconds - (end_time - begin_time).seconds
        print 'need time sleep:%s' % diff
        if diff > 0:
            time.sleep(diff)
        # 激活
        has_active_payments = auto_review.automatic_activate_for_mch_ids(all_auth_mch_ids, datetime.now())
        # 通知
        auto_review.callback_and_nofity_mch(all_auth_mch_ids)
    print 'end'


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(main)
    # dt_id = get_dt_id()
    # # offset = 0
    # # while True:
    # #     print 'start 100 mch'
    # #     mch_ids = auto_review.get_dt_un_auth_mch(dt_id, offset)
    # #     if mch_ids:
    # #         offset = mch_ids[-1]
    # #         mch_ids = [mch_id[0] for mch_id in mch_ids]
    # #         auto_review.automatic_review(mch_ids)
    # #     else:
    # #         break
    #
    # print 'auto review mch'
    # print 'start 100 mch'
    # mch_ids = auto_review.get_dt_un_auth_mch(dt_id)
    # auto_review.automatic_review(mch_ids)
