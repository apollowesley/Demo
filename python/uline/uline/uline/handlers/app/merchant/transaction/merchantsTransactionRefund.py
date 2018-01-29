# -*- coding: utf-8 -*-
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import MchAdminHandler
from .form import MerchantRefundSearch
from datetime import timedelta
from uline.public.constants import WX_REFUND_STATE, PAY_CHANNEL
from uline.public.permit import check_permission


class MerchantsTransactionRefundHandler(MchAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantRefundSearch(self)
        if not self.form.validate():
            self.redirect('/merchant/transaction/refund')
            return
        self.pageindex = int(self.get_argument("p", 1))

    @asynchronous
    @gen.coroutine
    def get(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('merchant/transaction/merchantRefund.html', navigate_html=navigate_html, data=data,
                    form=self.form, total_num=total_number, all_total_fee=all_total_fee)

    @asynchronous
    @gen.coroutine
    def post(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('merchant/transaction/merchantRefund.html', navigate_html=navigate_html, data=data,
                    form=self.form, total_num=total_number, all_total_fee=all_total_fee)

    @gen.coroutine
    def db_execute(self, form, offset):
        # todo 优化查询逻辑
        '''
        多数据库多表联查
            1. 如果有商户名或者渠道名 先从uline出数据 再从uline_trade配对相关数据
            2. 如果没有商户名或者渠道名 先从uline_trade查出数据(这一步当数据多的时候会很卡，后续优化) 再从uline中配对相关数据
        :param form:
        :param offset:
        :return:
        '''
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None

        out_trade_no = form.out_trade_no.data or None
        mch_trade_no = form.mch_trade_no.data or None
        transaction_id = form.transaction_id.data or None

        refund_status = form.refund_status.data or None
        mch_refund_no = form.mch_refund_no.data or None
        out_refund_no = form.out_refund_no.data or None
        refund_id = form.refund_id.data or None
        channel = form.channel.data or None

        ret, total = [], 0

        mch_id = self.current_user

        search_count = False

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)
            if create_at_start and create_at_end - create_at_start < timedelta(21):
                search_count = True

        ul_query = """select
                       mch_name
                       from mch_inlet_info
                       where mch_id=%(mch_id)s
                       """
        ul_ret = self.db.selectSQL(ul_query, {"mch_id": mch_id})
        ul_ret = list(ul_ret)

        res = []

        tb_query = """select
                ul_mch_id,
                to_char(created_at, 'YYYY-MM-DD HH24:MI:SS'),
                out_trade_no,
                mch_trade_no,
                op_user_id,
                refund_id,
                out_refund_no,
                refund_fee,
                refund_status,
                channel,
                COUNT(*) OVER () AS total
                from order_refunds
                where ul_mch_id=%(ul_mch_id)s
                and (refund_status=%(refund_status)s or %(refund_status)s is null)
                and (channel=%(channel)s or %(channel)s is null)
                and (mch_refund_no ~ %(mch_refund_no)s or %(mch_refund_no)s is null)
                and (out_refund_no ~ %(out_refund_no)s or %(out_refund_no)s is null)
                and (refund_id ~ %(refund_id)s or %(refund_id)s is null)
                and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                and (transaction_id ~ %(transaction_id)s or %(transaction_id)s is null)
                and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                and (created_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                or %(create_at_start)s is null or %(create_at_end)s is null)
                order by created_at desc
                offset %(offset)s rows fetch next 10 rows only;"""

        search_count_query = """select sum(refund_fee) from order_refunds
                where ul_mch_id=%(ul_mch_id)s
                and (refund_status=%(refund_status)s or %(refund_status)s is null)
                and (channel=%(channel)s or %(channel)s is null)
                and (mch_refund_no ~ %(mch_refund_no)s or %(mch_refund_no)s is null)
                and (out_refund_no ~ %(out_refund_no)s or %(out_refund_no)s is null)
                and (refund_id ~ %(refund_id)s or %(refund_id)s is null)
                and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                and (transaction_id ~ %(transaction_id)s or %(transaction_id)s is null)
                and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                and (created_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                or %(create_at_start)s is null or %(create_at_end)s is null)"""

        tb_ret = self.tdb.selectSQL(tb_query, {
            'ul_mch_id': str(mch_id),
            'refund_status': refund_status,
            'channel': channel,
            'mch_refund_no': mch_refund_no,
            'out_refund_no': out_refund_no,
            'refund_id': refund_id,
            'out_trade_no': out_trade_no,
            'transaction_id': transaction_id,
            'mch_trade_no': mch_trade_no,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'offset': offset}, fetchone=False)  # 每页显示10条数据

        if tb_ret:
            data = yield self.gen_tb_ret(tb_ret, ul_ret)
            data = yield self.deal_data(data)
            ret, total = data, data[0][-2]  # 数据,总数
            res.extend([ret, total])
        else:
            res.extend([[], 0])
        if search_count:
            search_ret = self.tdb.selectSQL(search_count_query, {
                'ul_mch_id': str(mch_id),
                'refund_status': refund_status,
                'channel': channel,
                'mch_refund_no': mch_refund_no,
                'out_refund_no': out_refund_no,
                'refund_id': refund_id,
                'out_trade_no': out_trade_no,
                'mch_trade_no': mch_trade_no,
                'transaction_id': transaction_id,
                'create_at_start': create_at_start,
                'create_at_end': create_at_end}, fetchone=True)  # 每页显示10条数据
            res.append(search_ret[0] / 100 if search_ret[0] else 0)
        else:
            res.extend(['--'])
        raise gen.Return(res)

    @gen.coroutine
    def gen_tb_ret(self, tb_ret, ul_ret, _type=None):
        data = []
        ret = [list(i) for i in tb_ret]
        for _d in ret:
            _d.extend(ul_ret)
            data.append(_d)
        raise gen.Return(data)

    @gen.coroutine
    def deal_data(self, data):
        for _d in data:
            _d[4] = self.get_mch_name_by_mch_id(_d[4]) if _d[4] else "接口发起"
            _d[7], _d[8], _d[9] = _d[7] / 100, WX_REFUND_STATE[_d[8]], PAY_CHANNEL[_d[9]]
        raise gen.Return(data)

    def get_mch_name_by_mch_id(self, mch_id):
        _query = 'select mch_name from mch_user where mch_id::VARCHAR = %(mch_id)s::VARCHAR'
        tb_ret = self.db.selectSQL(_query, {'mch_id': mch_id})
        _name = '%s(%s)' % (tb_ret[0], mch_id) if tb_ret else "接口发起"
        return _name
