# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import IntBkAdminHandler
from .form import MerchantSearch
from datetime import timedelta
from uline.public.common import get_week_range
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH
from uline.public import auth_util, constants
from uline.utils.dayzero import form_verify
from uline.utils.jingdong.jd_validation import check_mch_has_jd_pay
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from sqlalchemy import desc
from uline.model.uline.other import AuthMchInfo
from uline.model.uline.base import uline_session


class MerchantInletIndexHandler(IntBkAdminHandler):

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.form = MerchantSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/inter_bank/inlet/mch')
            return
        self.pageindex = int(self.get_argument("p", 1))
        self.open_review = FEATURE_SWITCH['REVIEW']
        self.d0_auth = FEATURE_SWITCH.get('D0_AUTH', False)
        self.jd_auth = FEATURE_SWITCH.get('JD_AUTH', False)

    def get(self):
        # get 请求时如果没有create_at_start和create_at_end，则默认查询最近7天
        if not self.form.create_at_start.data and not self.form.create_at_end.data and self.pageindex == 1:
            create_at_start, create_at_end = get_week_range()
            self.form.create_at_start.data = create_at_start
            self.form.create_at_end.data = create_at_end
        self.data, self.total_number = self.db_execute(self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('inter_bank/inlet/merchant.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=self.open_review)

    def generate_unchanged_render_params(self):
        return {
            'print_status': auth_util.print_auth_status
        }

    def post(self):
        self.data, self.total_number = self.db_execute(self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('inter_bank/inlet/merchant.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=self.open_review)

    def db_execute(self, form, offset):
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        mch_name = form.mch_name.data or None
        auth_status = form.auth_status.data or None
        dt_name = form.dt_name.data or None
        dt_id = form.dt_id.data or None
        mch_id = form.mch_id.data or None

        if not self.open_review and auth_status == 3:
            auth_status = (constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY)
        elif not self.open_review and auth_status == 1:
            auth_status = (constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD)
        else:
            auth_status = (auth_status,)

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        query = """select mch.mch_id,mch.mch_name,mch.mch_shortname,mch.activated_status,mch.auth_status,dt.dt_name,z.auth_user, COUNT(*) OVER () AS total
                from mch_inlet_info as mch
                  inner join dt_user as dt on mch.dt_id=dt.dt_id
                  inner join (select auth_user ,mch_id from auth_mch_info as a1 where not exists(select 1 from auth_mch_info as a2
                    where a2.mch_id= a1.mch_id and a2.create_at > a1.create_at)) as z on z.mch_id = mch.mch_id
                where (mch.activated_status=%(activated_status)s or %(activated_status)s is null)
                and (mch.auth_status in %(auth_status)s or %(auth_status)s is null)
                and (mch.mch_name ~ E%(mch_name)s or %(mch_name)s = '')
                and (dt.dt_name ~ E%(dt_name)s or %(dt_name)s = '')
                and (dt.dt_id::VARCHAR ~ E%(dt_id)s or %(dt_id)s = '')
                and (mch.mch_id::VARCHAR ~ E%(mch_id)s or %(mch_id)s = '')
                and (mch.cs_id is null)
                AND (mch.bk_id=%(bk_id)s)
                and (mch.create_at between %(create_at_start)s::timestamp
                  and %(create_at_end)s::timestamp or %(create_at_start)s is null or %(create_at_end)s is null)
                order by mch.create_at desc
                offset %(offset)s rows fetch next 10 rows only;
                """

        ret = self.db.selectSQL(query, {
            'activated_status': activated_status,
            'auth_status': auth_status,
            'mch_name': self.db.escape(mch_name),
            'mch_id': self.db.escape(mch_id),
            'dt_name': self.db.escape(dt_name),
            'dt_id': self.db.escape(dt_id),
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'bk_id': self.current_user,
            'offset': offset}, fetchone=False)  # 每页显示10条数据
        if ret:
            ret_list = []
            sql = """select comment from auth_mch_info where mch_id=%s ORDER BY id desc LIMIT 1"""
            risk_sql = """select count(*) from merchant_risk
                                       where sys_id=%s and sys_type_id=%s and has_risk>0 and status=1"""
            for i in ret:
                i = list(i)
                not_same_user = 1
                if self.open_review:
                    last_auth_user = self.get_last_auth_user(i[0])
                    # current_user = self.session.get('bk_id')
                    current_user = self.session.get('employee_id')
                    not_same_user = 0 if current_user in last_auth_user else 1
                i[-2] = not_same_user

                is_d0_mch = form_verify.check_mch_is_d0(i[0])
                id_jd_mch = check_mch_has_jd_pay(i[0])
                not_auth = False
                # 如果包含京东或者d0则不支持审核
                if (is_d0_mch and not self.d0_auth) or (id_jd_mch and not self.jd_auth):
                    not_auth = True
                i.insert(-1, not_auth)

                comment = self.db.selectSQL(sql, (i[0],))[0]
                i.insert(-1, comment)

                mch_id = i[0]
                has_risk = self.db.selectSQL(risk_sql, (mch_id, 'mch'))[0]
                i.insert(-1, has_risk)
                ret_list.append(tuple(i))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0

    def auth_userid(self, auth_user):
        selSql = """select bk_id from bk_user where email=%s"""
        db_ret = self.db.selectSQL(selSql, (auth_user,))
        if db_ret:
            return db_ret[0]

    def get_last_auth_user(self, mch_id):
        # last_auth_query = """select bk_id, auth_user, auth_status from auth_mch_info
        #                      left join bk_user on bk_user.email=auth_mch_info.auth_user
        #                      where mch_id=%s and auth_status in %s
        #                      order by id desc limit 1"""
        # result = self.db.selectSQL(last_auth_query,
        #                            (mch_id, (constants.AUTH_STATUS_PREVIEWD, constants.AUTH_STATUS_SUBMIT)),
        #                            use_dict=True)
        # if result:
        #     return result[0]
        auth_mch_info = uline_session.query(AuthMchInfo).filter(AuthMchInfo.mch_id == mch_id).order_by(
            desc(AuthMchInfo.create_at)).first()
        if auth_mch_info:
            email = auth_mch_info.auth_user
            sys_type_id = self.session["sys_type_id"]
            last_employee = uline_session.query(Employee).join(UserProfile, UserProfile.id == Employee.user_id).\
                filter(UserProfile.email == email, Employee.sys_type_id == sys_type_id).all()
            if last_employee:
                ids = [employee.id for employee in last_employee]
                return ids
            else:
                return []
        else:
            return []
