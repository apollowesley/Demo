# -*- coding: utf-8 -*-
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import MerchantTradeSearch
from datetime import timedelta
from uline.public.common import get_month_range
from uline.settings import FEATURE_SWITCH
from uline.public.constants import WX_TRADE_TYPE, WX_TRADE_STATE, PAY_CHANNEL
from uline.public.permit import check_permission


class CsTransactionTradeHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.h5 = FEATURE_SWITCH.get('H5')
        self.form = MerchantTradeSearch(self)
        self.chain_id = self.current_user
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/chain/transaction/trade')
            return
        self.pageindex = int(self.get_argument("p", 1))

    @asynchronous
    @gen.coroutine
    def get(self):
        if not self.form.complete_at_start.data and not self.form.complete_at_end.data and self.pageindex == 1:
            complete_at_start, complete_at_end = get_month_range()
            self.form.complete_at_start.data = complete_at_start
            self.form.complete_at_end.data = complete_at_end
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('chain/transaction/csTrade.html', navigate_html=navigate_html, data=data,
                    form=self.form, total_num=total_number, all_total_fee=all_total_fee, h5=self.h5)

    @asynchronous
    @gen.coroutine
    def post(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('chain/transaction/csTrade.html', navigate_html=navigate_html, data=data,
                    form=self.form, total_num=total_number, all_total_fee=all_total_fee, h5=self.h5)

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
        complete_at_start = form.complete_at_start.data or None
        complete_at_end = form.complete_at_end.data or None
        trade_type = form.trade_type.data or None
        trade_state = form.trade_state.data or None
        # 因为 orders表中，微信和支付宝的支付成功状态不一致，所以当trade_state=SUCCESS，需加上TRADE_SUCCESS
        if trade_state:
            if trade_state == 'SUCCESS':
                trade_state = ('SUCCESS', 'TRADE_SUCCESS')
            else:
                trade_state = tuple(trade_state)
        else:
            trade_state = ('SUCCESS', 'TRADE_SUCCESS', 'REFUND', 'NOTPAY',
                           'CLOSED', 'REVOKED', 'USERPAYING', 'PAYERROR', '')
        mch_name = form.mch_name.data or None
        mch_trade_no = form.mch_trade_no.data or None
        out_trade_no = form.out_trade_no.data or None
        wx_transaction_id = form.wx_transaction_id.data or None
        channel = form.channel.data or None
        mch_id = form.mch_id.data or None
        chain_sub_id = form.chain_sub_id.data or None
        if trade_type:
            if trade_type.startswith('ALIPAY'):
                channel = 'alipay'
                trade_type = trade_type[7:]
            elif trade_type.startswith('JDPAY'):
                channel = 'jdpay'
                trade_type = trade_type[6:]
            else:
                channel = 'weixin'

        ret, total = [], 0

        search_count = False

        if complete_at_end and complete_at_start:
            if complete_at_end - complete_at_start < timedelta(21):
                search_count = True

        ul_query = """select
                   mch_id,
                   mch_name,
                   mch_shortname
                   from mch_inlet_info
                   where cs_id=%(chain_id)s
                   and (mch_name ~ E%(mch_name)s or %(mch_name)s = '')
                   and (dt_sub_id = %(chain_sub_id)s or %(chain_sub_id)s is null)
                   and (mch_id::VARCHAR ~ E%(mch_id)s or %(mch_id)s = '');
                   """
        ul_ret = self.db.selectSQL(ul_query,
                                   {"mch_name": self.db.escape(mch_name),
                                    "chain_id": self.chain_id,
                                    "mch_id": self.db.escape(mch_id),
                                    'chain_sub_id': chain_sub_id},
                                   fetchone=False)

        ul_rets = {str(i[0]): list(i)[1:] for i in ul_ret}

        ul_mch_id = [str(i[0]) for i in ul_ret] if ul_ret else []

        dt_query = """select dt_id from mch_inlet_info where cs_id=%(chain_id)s;"""
        dt_query_dict = {
            "chain_id": self.chain_id,
        }
        dt_ret = self.db.selectSQL(dt_query, dt_query_dict, fetchone=True)
        dt_ids = [str(i) for i in dt_ret] if dt_ret else []
        dt_ids = tuple(dt_ids)

        res = []

        if ul_mch_id:
            ul_mch_id = tuple(ul_mch_id)

            use_dt_in_query = 'and dt_id in %(dt_ids)s'

            tb_query = """select
                    ul_mch_id,
                    to_char(complete_at, 'YYYY-MM-DD HH24:MI:SS'),
                    out_trade_no,
                    mch_trade_no,
                    trade_state,
                    trade_type,
                    total_fee,
                    channel,
                    COUNT(*) OVER () AS total
                    from orders
                    where complete_at is not null
                    and (complete_at!='0001-01-01 00:00:00.000000')
                    {use_dt_in_query}
                    and ul_mch_id in %(ul_mch_id)s
                    and (%(trade_state)s is null or trade_state in %(trade_state)s)
                    and (trade_type=%(trade_type)s or %(trade_type)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (wx_transaction_id ~ %(wx_transaction_id)s or %(wx_transaction_id)s is null)
                    and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                    or %(complete_at_start)s is null or %(complete_at_end)s is null)
                    order by id desc
                    offset %(offset)s rows fetch next 10 rows only;
                    """

            search_count_query = """select sum(total_fee) from orders
                    where ul_mch_id in %(ul_mch_id)s
                    and complete_at is not null
                    and (complete_at!='0001-01-01 00:00:00.000000')
                    and (trade_state in %(trade_state)s or %(trade_state)s is null)
                    and (trade_type=%(trade_type)s or %(trade_type)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                    and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                    and (wx_transaction_id ~ %(wx_transaction_id)s or %(wx_transaction_id)s is null)
                    and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                    or %(complete_at_start)s is null or %(complete_at_end)s is null);
                    """

            tb_ret = self.tdb.selectSQL(tb_query.format(use_dt_in_query=use_dt_in_query), {
                'ul_mch_id': ul_mch_id,
                'dt_ids': dt_ids,
                'trade_type': trade_type,
                'trade_state': trade_state,
                'channel': channel,
                'out_trade_no': out_trade_no,
                'mch_trade_no': mch_trade_no,
                'wx_transaction_id': wx_transaction_id,
                'complete_at_start': complete_at_start,
                'complete_at_end': complete_at_end,
                'offset': offset}, fetchone=False)  # 每页显示10条数据

            if tb_ret:
                # data = yield self.gen_tb_ret(tb_ret, ul_rets)
                # data = yield self.deal_data(data)
                # ret, total = data, data[0][-3]  # 数据,总数
                # res.extend([ret, total])
                data = yield self.gen_tb_ret(tb_ret, ul_rets)
                # 数据,总数
                ret, total = data, data[0][-3]

                res.extend([ret, total])
            else:
                res.extend([[], 0])

            if search_count:
                search_ret = self.tdb.selectSQL(search_count_query, {
                    'ul_mch_id': ul_mch_id,
                    'trade_type': trade_type,
                    'trade_state': trade_state,
                    'channel': channel,
                    'out_trade_no': out_trade_no,
                    'mch_trade_no': mch_trade_no,
                    'wx_transaction_id': wx_transaction_id,
                    'complete_at_start': complete_at_start,
                    'complete_at_end': complete_at_end}, fetchone=True)
                res.append(search_ret[0] / 100 if search_ret and search_ret[0] else 0)
            else:
                res.extend(['--'])
        else:
            res = [[], 0, 0]

        raise gen.Return(res)

    # @gen.coroutine
    # def gen_tb_ret(self, tb_ret, ul_ret):
    #     data = []
    #     ret = [list(i) for i in tb_ret]
    #     for tb_data in ret:
    #         for ul_data in ul_ret:
    #             if int(tb_data[0]) == ul_data[0]:
    #                 tb_data.extend([ul_data[1], ul_data[2]])
    #                 data.append(tb_data)
    #     raise gen.Return(data)

    @gen.coroutine
    def gen_tb_ret(self, tb_ret, ul_ret):
        data = []
        for tb_data in tb_ret:
            tb_data = list(tb_data)
            if ul_ret.get(tb_data[0]):
                tb_data.extend(ul_ret[tb_data[0]])
                tb_data = yield self.enhance_deal_data(tb_data)
                data.append(tb_data)
        raise gen.Return(data)

    @gen.coroutine
    def enhance_deal_data(self, _d):
        if _d[4]:
            _d[4] = WX_TRADE_STATE.get(str(_d[4]))
        if _d[5]:
            _d[5] = u'JS支付' if _d[7] == 'alipay' and str(
                _d[5]) == 'JSAPI' else WX_TRADE_TYPE[str(_d[5])]
        if _d[6]:
            _d[6] = _d[6] / 100
        if _d[7]:
            _d[7] = PAY_CHANNEL[_d[7]]
        raise gen.Return(_d)

    # @gen.coroutine
    # def deal_data(self, data):
    #     for _d in data:
    #         if _d[4]:
    #             _d[4] = WX_TRADE_STATE[str(_d[4])]
    #         if _d[5]:
    #             _d[5] = u'JS支付' if _d[7] == 'alipay' and str(
    #                 _d[5]) == 'JSAPI' else WX_TRADE_TYPE[str(_d[5])]
    #         if _d[6]:
    #             _d[6] = _d[6] / 100
    #         if _d[7]:
    #             _d[7] = PAY_CHANNEL[_d[7]]
    #     raise gen.Return(data)
    def deal_data(self, data):
        for _d in data:
            if _d[4]:
                _d[4] = WX_TRADE_STATE[str(_d[4])]
            if _d[5]:
                _d[5] = u'JS支付' if _d[7] in ['alipay', 'jdpay'] and str(
                    _d[5]) == 'JSAPI' else WX_TRADE_TYPE[str(_d[5])]
            if _d[6]:
                _d[6] = _d[6] / 100
            if _d[7]:
                _d[7] = PAY_CHANNEL[_d[7]]
        raise gen.Return(data)
