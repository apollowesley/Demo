#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from tornado import gen, ioloop


def get_dt_id():
    """从命令行获取渠道商id"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('dt_id', metavar='DT_ID', type=str,
                        help='input mch_id')
    args = parser.parse_args()
    return args.dt_id


# import uline.backend.bank.automatic_review_activate as auto_review
import uline.backend.bank.automatic_review_activate_6_2 as auto_review


@gen.coroutine
def main():
    dt_id = get_dt_id()
    # dt_ids = [10000005554, 10000006774, 10000063337, 10000050727, 10000037107, 10000045429, 10000056667,
    #           10000101520, 10000086344]
    # for dt_id in dt_ids:
    if dt_id:
        mch_ids = auto_review.get_dt_un_auth_mch(dt_id)
        print len(mch_ids)
        if mch_ids:
            mch_ids = [mch_id for mch_id in mch_ids]
            yield auto_review.automatic_review(mch_ids)

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
