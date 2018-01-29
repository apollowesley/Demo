# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import ChainAdminHandler
from .form import MerchantBalanceSearch
from datetime import datetime, timedelta
from uline.public.common import get_week_range
from uline.public.constants import TO_PAY, PAY_CHANNEL
from uline.public.permit import check_permission


class CsBalanceIndexHandler(ChainAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantBalanceSearch(self)
        self.form.chain_id = self.current_user
        if not self.form.validate():
            self.redirect('/chain/balance/mch')
            return
        self.pageindex = int(self.get_argument("p", 1))

    def get(self):
        # get 请求时如果没有create_at_start和create_at_end，则默认查询最近7天
        if not self.form.create_at_start.data and not self.form.create_at_end.data and self.pageindex == 1:
            create_at_start, create_at_end = get_week_range()
            self.form.create_at_start.data = create_at_start
            self.form.create_at_end.data = create_at_end
        self.data, self.total_number = self.db_execute((self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('chain/balance/csBalance.html', navigate_html=navigate_html, data=self.data,
                    form=self.form, total_num=self.total_number)

    def post(self):
        self.data, self.total_number = self.db_execute((self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('chain/balance/csBalance.html', navigate_html=navigate_html, data=self.data,
                    form=self.form, total_num=self.total_number)

    def db_execute(self, offset):
        """
        :param offset:
        :return:
        """
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        pay_status = self.form.pay_status.data or None
        mch_name = self.form.mch_name.data or None
        channel = self.form.channel.data or None
        mch_id = self.form.mch_id.data or None
        chain_sub_id = self.form.chain_sub_id.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """select
                   to_char(mdbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
                   mdbi.need_pay_time,
                   mii.mch_name,
                   mii.mch_shortname,
                   mdbi.rcvacctname,
                   mdbi.channel,
                   mdbi.rcvacctno,
                   mdbi.tranamt,
                   mdbi.pay_status,
                   mdbi.mch_daily_balance_no,
                   count(*) over () as total
                   from mch_daily_balance_info as mdbi
                   inner join mch_inlet_info as mii on mii.mch_id = mdbi.mch_id
                   inner join mch_balance as mb on mb.mch_id = mdbi.mch_id
                   where mii.cs_id=%(chain_id)s
                   and cs_id is not null
                   and mdbi.tranamt > 0
                   and (mdbi.pay_status=%(pay_status)s or %(pay_status)s is null)
                   and (mdbi.channel=%(channel)s or %(channel)s is null)
                   and (mii.dt_sub_id = %(chain_sub_id)s or %(chain_sub_id)s is null)
                   and (mii.mch_name ~ E%(mch_name)s or %(mch_name)s = '')
                   and (mii.mch_id::VARCHAR ~ E%(mch_id)s or %(mch_id)s = '')
                   and (mdbi.pay_start_time BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
                   OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                   ORDER BY mdbi.create_at desc
                   OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"""
        ret = self.db.selectSQL(query, {
            'pay_status': pay_status,
            'channel': channel,
            'mch_name': self.db.escape(mch_name),
            'mch_id': self.db.escape(mch_id),
            'chain_id': self.current_user,
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'offset': offset,
            'chain_sub_id': chain_sub_id,
        }, fetchone=False)

        if ret:
            if len(ret) > 0:
                ret = [list(i) for i in ret]
                for index in range(0, len(ret)):
                    # T+1结算方式
                    ret[index][1] -= timedelta(days=1)
                    ret[index][1] = datetime.strftime(
                        ret[index][1], '%Y-%m-%d')
                    ret[index][5], ret[index][-3], ret[index][-4] = PAY_CHANNEL[ret[index][5]], TO_PAY[str(ret[index][-3])], \
                        ret[index][-4] / 100
                return ret, ret[0][-1]  # 数据,总数
        return ret, 0
