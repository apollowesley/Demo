# -*- coding: utf-8 -*-
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import IntBkAdminHandler
from .form import MerchantRefundSearch
from datetime import timedelta
from uline.public.constants import WX_REFUND_STATE, PAY_CHANNEL
from uline.public.permit import check_permission


class MerchantsTransactionRefundHandler(IntBkAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantRefundSearch(self)
        if not self.form.validate():
            self.redirect('/inter_bank/transaction/refund')
            return
        self.pageindex = int(self.get_argument('p', '1')) if self.get_argument('p', '1').isdigit() else 1

    @asynchronous
    @gen.coroutine
    def get(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('inter_bank/transaction/merchantRefund.html', navigate_html=navigate_html, data=data, form=self.form,
                    total_num=total_number, all_total_fee=all_total_fee)

    @asynchronous
    @gen.coroutine
    def post(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('inter_bank/transaction/merchantRefund.html', navigate_html=navigate_html, data=data, form=self.form,
                    total_num=total_number, all_total_fee=all_total_fee)

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
        mch_name = form.mch_name.data or None
        dt_name = form.dt_name.data or None
        dt_id = form.dt_id.data or None
        mch_id = form.mch_id.data or None

        out_trade_no = form.out_trade_no.data or None
        mch_trade_no = form.mch_trade_no.data or None
        transaction_id = form.transaction_id.data or None

        refund_status = form.refund_status.data or None
        mch_refund_no = form.mch_refund_no.data or None
        out_refund_no = form.out_refund_no.data or None
        refund_id = form.refund_id.data or None
        channel = form.channel.data or None
        cs_mch_shortname = form.cs_mch_shortname.data or None
        cs_mch_id = form.cs_mch_id.data or None

        ret, total = [], 0

        search_count = False

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)
            if create_at_start and create_at_end - create_at_start < timedelta(21):
                search_count = True

        ul_query = """select
                       mch_inlet_info.mch_id,
                       mch_inlet_info.mch_name,
                       mch_inlet_info.mch_shortname,
                        dt_inlet_info.dt_short_name,
                        mch_inlet_info.cs_id,
                       dt_user.dt_name,
                       dt_inlet_info.dt_name
                       from mch_inlet_info
                       inner join dt_user on dt_user.dt_id = mch_inlet_info.dt_id
                       left join dt_inlet_info on dt_inlet_info.dt_id = mch_inlet_info.cs_id
                       where (dt_user.dt_name ~ E%(dt_name)s or %(dt_name)s = '')
                        and (mch_inlet_info.bk_id = %(bk_id)s)
                      and (mch_inlet_info.mch_id::VARCHAR ~ E%(mch_id)s::VARCHAR or %(mch_id)s::VARCHAR is null)
                      and (mch_inlet_info.mch_shortname ~ E%(cs_mch_shortname)s or %(cs_mch_shortname)s is null)
                      and (mch_inlet_info.mch_name ~ E%(mch_name)s or %(mch_name)s is null)
                        {find_type}
                       and (dt_user.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '');
                       """

        query_dict = {
            "dt_name": self.db.escape(dt_name),
            "dt_id": self.db.escape(dt_id),
            'mch_name': self.db.escape(mch_name),
            'cs_mch_shortname': self.db.escape(cs_mch_shortname),
            'mch_id': self.db.escape(mch_id),
            'bk_id': self.get_current_user()
        }

        query_dict.update({'cs_mch_shortname': self.db.escape(cs_mch_shortname),
                           'mch_id': self.db.escape(cs_mch_id)}) if cs_mch_shortname or cs_mch_id else \
            query_dict.update({'mch_id': self.db.escape(mch_id)})

        if cs_mch_id:
            find_type = "and mch_inlet_info.cs_id is not null"
        else:
            find_type = "and mch_inlet_info.cs_id is null" if mch_name or mch_id else ""
        ul_ret = self.db.selectSQL(ul_query.format(
            find_type=find_type), query_dict, fetchone=False)

        ul_mch_id = [str(i[0]) for i in ul_ret] if ul_ret else []

        res = []

        if ul_mch_id:
            ul_mch_id = tuple(ul_mch_id)

            tb_query = """select
                    ul_mch_id,
                    to_char(created_at, 'YYYY-MM-DD HH24:MI:SS'),
                    transaction_id,
                    out_trade_no,
                    refund_id,
                    out_refund_no,
                    refund_fee,
                    refund_status,
                    channel,
                    COUNT(*) OVER () AS total
                    from order_refunds
                    where ul_mch_id in %(ul_mch_id)s
                    and (refund_status=%(refund_status)s or %(refund_status)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    and (mch_refund_no ~ %(mch_refund_no)s or %(mch_refund_no)s is null)
                    and (out_refund_no ~ %(out_refund_no)s or %(out_refund_no)s is null)
                    and (refund_id ~ %(refund_id)s or %(refund_id)s is null)
                    and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (transaction_id ~ %(transaction_id)s or %(transaction_id)s is null)
                    and (created_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                    or %(create_at_start)s is null or %(create_at_end)s is null)
                    order by created_at desc
                    offset %(offset)s rows fetch next 10 rows only;"""

            search_count_query = """select sum(refund_fee) from order_refunds WHERE ul_mch_id in %(ul_mch_id)s
                    and (refund_status=%(refund_status)s or %(refund_status)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    and (mch_refund_no ~ %(mch_refund_no)s or %(mch_refund_no)s is null)
                    and (out_refund_no ~ %(out_refund_no)s or %(out_refund_no)s is null)
                    and (refund_id ~ %(refund_id)s or %(refund_id)s is null)
                    and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (transaction_id ~ %(transaction_id)s or %(transaction_id)s is null)
                    and (created_at between %(create_at_start)s::timestamp and %(create_at_end)s::timestamp
                    or %(create_at_start)s is null or %(create_at_end)s is null);
                """

            tb_ret = self.tdb.selectSQL(tb_query, {
                'ul_mch_id': ul_mch_id,
                'refund_status': refund_status,
                'channel': channel,
                'mch_refund_no': mch_refund_no,
                'out_refund_no': out_refund_no,
                'refund_id': refund_id,
                'out_trade_no': out_trade_no,
                'mch_trade_no': mch_trade_no,
                'transaction_id': transaction_id,
                'create_at_start': create_at_start,
                'create_at_end': create_at_end,
                'offset': offset}, fetchone=False)  # 每页显示10条数据

            if tb_ret:
                data = yield self.gen_tb_ret(tb_ret, ul_ret)
                data = yield self.deal_data(data)
                ret, total = data, data[0][-7]  # 数据,总数
                res.extend([ret, total])
            else:
                res.extend([[], 0])

            if search_count:
                search_ret = self.tdb.selectSQL(search_count_query, {
                    'ul_mch_id': ul_mch_id,
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
        else:
            res = [[], 0, 0]

        raise gen.Return(res)

    @gen.coroutine
    def gen_tb_ret(self, tb_ret, ul_ret):
        data = []
        ret = [list(i) for i in tb_ret]
        for tb_data in ret:
            for ul_data in ul_ret:
                if int(tb_data[0]) == ul_data[0]:
                    tb_data.extend(
                        [ul_data[1], ul_data[2], ul_data[3], ul_data[4], ul_data[5], ul_data[6]])
                    data.append(tb_data)
        raise gen.Return(data)

    @gen.coroutine
    def deal_data(self, data):
        for _d in data:
            _d[6], _d[7], _d[8] = _d[6] / \
                100, WX_REFUND_STATE.get(_d[7]), PAY_CHANNEL.get(_d[8])
        raise gen.Return(data)
