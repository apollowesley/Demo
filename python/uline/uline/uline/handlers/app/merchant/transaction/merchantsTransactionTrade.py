# -*- coding: utf-8 -*-
from __future__ import division
from tornado.web import authenticated, asynchronous
from tornado import gen
from uline.handlers.baseHandlers import MchAdminHandler
from .form import MerchantTradeSearch
from datetime import timedelta
from uline.public.common import get_month_range
from uline.settings import FEATURE_SWITCH
from uline.public.constants import WX_TRADE_TYPE, WX_TRADE_STATE, PAY_CHANNEL
from uline.public.permit import check_permission


class MerchantsTransactionTradeHandler(MchAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.h5 = FEATURE_SWITCH.get('H5')
        self.form = MerchantTradeSearch(self)
        # 查询参数不合法
        if not self.form.validate():
            self.redirect('/merchant/transaction/trade')
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
        self.render('merchant/transaction/merchantTrade.html', navigate_html=navigate_html, data=data, form=self.form,
                    total_num=total_number, all_total_fee=all_total_fee, h5=self.h5)

    @asynchronous
    @gen.coroutine
    def post(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        data, total_number, all_total_fee = ret[0], ret[1], ret[2]
        navigate_html = self.get_navigate_html(total_number)
        self.render('merchant/transaction/merchantTrade.html', navigate_html=navigate_html, data=data, form=self.form,
                    total_num=total_number, all_total_fee=all_total_fee, h5=self.h5)

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
        out_trade_no = form.out_trade_no.data or None
        mch_trade_no = form.mch_trade_no.data or None
        wx_transaction_id = form.wx_transaction_id.data or None
        channel = form.channel.data or None
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
        mch_id = self.current_user

        search_count = False

        if complete_at_end and complete_at_start:
            if complete_at_end - complete_at_start < timedelta(21):
                search_count = True

        ul_query = """select
                   mch_name
                   from mch_inlet_info
                   where mch_id=%(mch_id)s
                   """
        ul_ret = self.db.selectSQL(ul_query, {"mch_id": mch_id})

        res = []

        count_ret = None

        use_no_query = ''

        # 当按照 out_trade_no、mch_trade_no和wx_transaction_id查询时，单独的count会导致更慢，所以写在一条sql
        if out_trade_no or mch_trade_no or wx_transaction_id:
            for k, v in {'out_trade_no': out_trade_no, 'mch_trade_no': mch_trade_no,
                         'wx_transaction_id': wx_transaction_id}.iteritems():
                if v:
                    use_no_query += 'and {}=%({})s'.format(k, k)
            tb_query = """select
                    ul_mch_id,
                    to_char(complete_at, 'YYYY-MM-DD HH24:MI:SS'),
                    out_trade_no,
                    mch_trade_no,
                    trade_state,
                    trade_type,
                    total_fee,
                    channel,
                    detail,
                    1
                    from orders
                    where (complete_at is not null)
                    and (complete_at!='0001-01-01 00:00:00.000000')
                    and ul_mch_id=%(ul_mch_id)s
                    and (trade_state in %(trade_state)s or %(trade_state)s is null)
                    and (trade_type=%(trade_type)s or %(trade_type)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    {use_no_query}
                    and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                    or %(complete_at_start)s is null or %(complete_at_end)s is null)
                    order by id desc
                    offset %(offset)s rows fetch next 10 rows only;
                    """
        else:
            tb_query = """select
                    ul_mch_id,
                    to_char(complete_at, 'YYYY-MM-DD HH24:MI:SS'),
                    out_trade_no,
                    mch_trade_no,
                    trade_state,
                    trade_type,
                    total_fee,
                    channel,
                    detail,
                    1
                    from orders
                    where (complete_at is not null)
                    and (complete_at!='0001-01-01 00:00:00.000000')
                    and ul_mch_id=%(ul_mch_id)s
                    and (%(trade_state)s is null or trade_state in %(trade_state)s)
                    and (trade_type=%(trade_type)s or %(trade_type)s is null)
                    and (channel=%(channel)s or %(channel)s is null)
                    {use_no_query}
                    and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                    or %(complete_at_start)s is null or %(complete_at_end)s is null)
                    order by id desc
                    offset %(offset)s rows fetch next 10 rows only;
                    """

            count_query = """select
                        count(complete_at)
                        from orders
                        where
                        (trade_state in %(trade_state)s or %(trade_state)s is null)
                        and ul_mch_id=%(ul_mch_id)s
                        and (complete_at!='0001-01-01 00:00:00.000000')
                        and (trade_type=%(trade_type)s or %(trade_type)s is null)
                        and (channel=%(channel)s or %(channel)s is null)
                        and (out_trade_no ~ %(out_trade_no)s or %(out_trade_no)s is null)
                        and (mch_trade_no ~ %(mch_trade_no)s or %(mch_trade_no)s is null)
                        and (wx_transaction_id ~ %(wx_transaction_id)s or %(wx_transaction_id)s is null)
                        and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                        or %(complete_at_start)s is null or %(complete_at_end)s is null)
                        LIMIT 1
                        """

            count_ret = self.tdb.selectSQL(count_query, {
                'ul_mch_id': str(mch_id),
                'trade_type': trade_type,
                'trade_state': trade_state,
                'channel': channel,
                'out_trade_no': out_trade_no,
                'mch_trade_no': mch_trade_no,
                'wx_transaction_id': wx_transaction_id,
                'complete_at_start': complete_at_start,
                'complete_at_end': complete_at_end,
                'offset': offset}, fetchone=True)

        search_count_query = """select sum(total_fee) from orders
                where ul_mch_id=%(ul_mch_id)s
                and (complete_at!='0001-01-01 00:00:00.000000')
                and complete_at is not null
                and (trade_state in %(trade_state)s or %(trade_state)s is null)
                and (trade_type=%(trade_type)s or %(trade_type)s is null)
                and (channel=%(channel)s or %(channel)s is null)
                {use_no_query}
                and (complete_at between %(complete_at_start)s::timestamp and %(complete_at_end)s::timestamp
                or %(complete_at_start)s is null or %(complete_at_end)s is null);
                """

        tb_ret = self.tdb.selectSQL(tb_query.format(use_no_query=use_no_query), {
            'ul_mch_id': str(mch_id),
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
            data = yield self.gen_tb_ret(tb_ret, ul_ret)
            ret, total = data, count_ret[0] if count_ret else data[0][-2]
            res.extend([ret, total])
        else:
            res.extend([[], 0])
        if search_count:
            search_ret = self.tdb.selectSQL(search_count_query.format(use_no_query=use_no_query), {
                'ul_mch_id': str(mch_id),
                'trade_type': trade_type,
                'trade_state': trade_state,
                'channel': channel,
                'out_trade_no': out_trade_no,
                'mch_trade_no': mch_trade_no,
                'wx_transaction_id': wx_transaction_id,
                'complete_at_start': complete_at_start,
                'complete_at_end': complete_at_end, }, fetchone=True)
            res.append(search_ret[0] / 100 if search_ret and search_ret[0] else 0)
        else:
            res.extend(['--'])
        raise gen.Return(res)

    @gen.coroutine
    def gen_tb_ret(self, tb_ret, ul_ret):
        data = []
        for tb_data in tb_ret:
            tb_data = list(tb_data)
            # if ul_ret.get(tb_data[0]):
            tb_data.extend(ul_ret)
            tb_data = yield self.enhance_deal_data(tb_data)
            data.append(tb_data)
        raise gen.Return(data)

    @gen.coroutine
    def enhance_deal_data(self, _d):
        if _d[4]:
            _d[4] = WX_TRADE_STATE[str(_d[4])]
        if _d[5]:
            _d[5] = u'JS支付' if _d[7] in ['alipay', 'jdpay'] and str(
                _d[5]) == 'JSAPI' else WX_TRADE_TYPE.get(str(_d[5]))
        if _d[6]:
            _d[6] = _d[6] / 100
        if _d[7]:
            _d[7] = PAY_CHANNEL[_d[7]]
        raise gen.Return(_d)

    # @gen.coroutine
    # def gen_tb_ret(self, tb_ret, ul_ret):
    #     data = []
    #     ret = [list(i) for i in tb_ret]
    #     for _d in ret:
    #         _d.extend(ul_ret)
    #         data.append(_d)
    #     raise gen.Return(data)
    #
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
