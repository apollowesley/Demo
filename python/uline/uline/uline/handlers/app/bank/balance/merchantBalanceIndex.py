# -*- coding: utf-8 -*-
from __future__ import division
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import BkAdminHandler
from .form import MerchantBalanceSearch
from datetime import timedelta, datetime
from uline.public.common import get_week_range
from uline.public.constants import TO_PAY, PAY_CHANNEL
from uline.public.permit import check_permission


class MerchantBalanceIndexIndexHandler(BkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantBalanceSearch(self)
        if not self.form.validate():
            self.redirect('/bank/balance/mch')
            return
        self.pageindex = int(self.get_argument("p", 1))

    def get(self):
        # get 请求时如果没有create_at_start和create_at_end，则默认查询最近7天
        if not self.form.create_at_start.data and not self.form.create_at_end.data and self.pageindex == 1:
            create_at_start, create_at_end = get_week_range()
            self.form.create_at_start.data = create_at_start
            self.form.create_at_end.data = create_at_end
        self.data, self.total_number = self.db_execute(
            self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/balance/merchantBalance.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, expand_type=0)

    def post(self):
        self.data, self.total_number = self.db_execute(
            self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('bank/balance/merchantBalance.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, expand_type=0)

    def db_execute(self, form, offset):
        """

        :param form:
        :param offset:
        :return:
        """
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        pay_status = form.pay_status.data or None
        mch_name = form.mch_name.data or None
        dt_name = form.dt_name.data or None
        channel = form.channel.data or None
        dt_id = form.dt_id.data or None
        mch_id = form.mch_id.data or None
        balance_account = form.balance_account.data or None
        cs_mch_shortname = form.cs_mch_shortname.data or None
        cs_mch_id = form.cs_mch_id.data or None
        expand_type = form.expand_type.data or None
        bk_id = form.bk_id.data or None
        bk_name = form.bk_name.data or None

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """select
                           to_char(mdbi.pay_start_time, 'YYYY-MM-DD HH24:MI:SS'),
                           mdbi.need_pay_time,
                           mii.mch_name,
                           mii.mch_shortname,
                           du.dt_name,
                           mdbi.rcvacctname,
                           mdbi.channel,
                           mb.balance_account,
                           mdbi.tranamt,
                           mdbi.pay_status,
                           mdbi.mch_daily_balance_no,
                           dii.dt_short_name,
                           mii.cs_id,
                           count(*) over () as total
                           from mch_daily_balance_info as mdbi
                           inner join mch_inlet_info as mii on mii.mch_id = mdbi.mch_id
                           inner join mch_balance as mb on mb.mch_id = mdbi.mch_id
                           inner join dt_user as du on du.dt_id = mii.dt_id
                           left join dt_inlet_info as dii on dii.dt_id = mii.cs_id
                           where mdbi.tranamt > 0
                            AND (mb.balance_account=%(balance_account)s or %(balance_account)s is null)
                           and (mdbi.pay_status=%(pay_status)s or %(pay_status)s is null)
                           and (mdbi.channel=%(channel)s or %(channel)s is null)
                           and (du.dt_name ~ E%(dt_name)s or %(dt_name)s = '')
                           and (du.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
                           and (mii.mch_id::VARCHAR ~ E%(mch_id)s::VARCHAR or %(mch_id)s::VARCHAR is null)
                           and (mii.mch_shortname ~ E%(cs_mch_shortname)s or %(cs_mch_shortname)s is null)
                           and (mii.mch_name ~ E%(mch_name)s or %(mch_name)s is null)
                          {find_type}
                            AND mii.bk_id IN (SELECT bk_id FROM bk_user WHERE (bk_type = %(expand_type)s OR %(expand_type)s IS NULL)
                            AND  (bk_id::VARCHAR ~ E%(bk_id)s OR %(bk_id)s IS NULL)
                            AND (bk_name ~ E%(bk_name)s OR %(bk_name)s IS NULL))
                           and (mdbi.pay_start_time BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP
                           OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL )
                           ORDER BY mdbi.create_at desc, mdbi.pay_start_time desc
                           OFFSET %(offset)s ROWS FETCH NEXT 10 ROWS ONLY;"""

        query_dict = {
            'pay_status': pay_status,
            'channel': channel,
            'dt_id': self.db.escape(dt_id),
            'dt_name': self.db.escape(dt_name),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'balance_account': balance_account,
            'mch_name': self.db.escape(mch_name),
            'cs_mch_shortname': self.db.escape(cs_mch_shortname),
            'mch_id': self.db.escape(mch_id),
            'expand_type': expand_type,
            'bk_id': self.db.escape(bk_id),
            'bk_name': self.db.escape(bk_name),
            'offset': offset
        }

        query_dict.update({'cs_mch_shortname': self.db.escape(cs_mch_shortname),
                           'mch_id': self.db.escape(cs_mch_id)}) if cs_mch_shortname or cs_mch_id else \
            query_dict.update({'mch_id': self.db.escape(mch_id)})

        if cs_mch_shortname or cs_mch_id:
            find_type = "and mii.cs_id is not null"
        else:
            find_type = "and mii.cs_id is null" if mch_name or mch_id else ""
        ret = self.db.selectSQL(query.format(
            find_type=find_type), query_dict, fetchone=False)

        if ret:
            ret = [list(i) for i in ret]
            for index in range(0, len(ret)):
                # T+1结算方式
                ret[index][1] -= timedelta(days=1)
                ret[index][1] = datetime.strftime(ret[index][1], '%Y-%m-%d')
                ret[index][6], ret[index][8], ret[index][9] = PAY_CHANNEL[ret[index][6]], ret[index][8] / 100, TO_PAY[
                    str(ret[index][9])]
            return ret, ret[0][-1]  # 数据,总数
        return ret, 0
