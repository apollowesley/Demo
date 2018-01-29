# -*- coding: utf-8 -*-
import tornado.web
import tornado.gen
from uline.handlers.baseHandlers import IntBkAdminHandler
from .form import CSSearch
from datetime import timedelta
from uline.settings import QR_SCAN_URL
from uline.settings import FEATURE_SWITCH

from uline.public.merchant_util import query_mch_inlet_infos, get_chain_info
from uline.public import auth_util, constants
from uline.public.permit import check_permission
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from sqlalchemy import desc
from uline.model.uline.other import AuthMchInfo
from uline.model.uline.base import uline_session


class CSInletIndexHandler(IntBkAdminHandler):
    """连锁门店列表

    Extends:
        BkAdminHandler
    """

    @tornado.web.authenticated
    @check_permission
    def prepare(self):
        self.open_review = FEATURE_SWITCH['REVIEW']
        self.form = CSSearch(self)
        # 查询参数不合法
        if not self.form.validate() and self.form.activated_status.data != None:
            self.redirect('/inter_bank/inlet/cs')
            return
        pageindex = int(self.get_argument("p", 1))
        self.data, self.total_number = self.db_execute(self.form, (pageindex - 1) * 10)

    def generate_unchanged_render_params(self):
        return {
            'print_status': auth_util.print_auth_status
        }

    def get(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('inter_bank/inlet/cs.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review)

    def post(self):
        open_review = FEATURE_SWITCH['REVIEW']
        navigate_html = self.get_navigate_html(self.total_number)
        self.render('inter_bank/inlet/cs.html', navigate_html=navigate_html, data=self.data, form=self.form,
                    total_num=self.total_number, QR_SCAN_URL=QR_SCAN_URL, open_review=open_review)

    def db_execute(self, form, offset):
        # 返回列表,过滤、分页
        create_at_start = form.create_at_start.data or None
        create_at_end = form.create_at_end.data or None
        activated_status = form.activated_status.data or None
        auth_status = form.auth_status.data or None

        mch_id = form.mch_id.data or None
        short_name = form.short_name.data or None

        cs_id = form.cs_id.data or None
        cs_name = form.cs_name.data or None

        if not self.open_review and auth_status == 3:
            auth_status = (constants.AUTH_STATUS_DENY, constants.AUTH_STATUS_FIRST_DENY)
        elif not self.open_review and auth_status == 1:
            auth_status = (constants.AUTH_STATUS_SUBMIT, constants.AUTH_STATUS_PREVIEWD)
        elif auth_status:
            auth_status = (auth_status,)

        conditions = {
            'create_at_start': create_at_start,
            'create_at_end': create_at_end,
            'activated_status': activated_status,
            'auth_status': auth_status,
            'mch_id': mch_id,
            'short_name': short_name,
            'offset': offset,
            'is_cs': True,
            'cs_id': cs_id,
            'cs_name': cs_name,
            'bk_id': self.current_user
        }

        # 因为end是0时0分,将它续一天┑(￣Д ￣)┍
        if create_at_end:
            create_at_end += timedelta(days=1)

        ret = query_mch_inlet_infos(self.db, conditions, offset, query_role=2)
        chain_map = dict()
        if ret:
            ret_list = []
            risk_sql = """select count(*) from merchant_risk
                                                               where sys_id=%s and sys_type_id=%s and has_risk>0 and status=1"""
            for mch_inlet_info in ret:
                mch_inlet_info = list(mch_inlet_info)
                mch_id = mch_inlet_info[0]
                auth_info = self.auth_userid(mch_id)
                # auth_user = ""
                # bk_id = 0
                # if auth_info:
                #     bk_id = auth_info[0]
                #     auth_user = auth_info[1]
                # current_user = self.session.get('bk_id')
                current_user = self.session["employee_id"]
                # auth_user = 0 if bk_id == current_user else 1
                auth_user = 0 if current_user in auth_info else 1
                mch_inlet_info.insert(-2, auth_user)
                has_risk = self.db.selectSQL(risk_sql, (mch_id, 'cs'))[0]
                cs_id = mch_inlet_info[-2]
                chain_info = chain_map.get(cs_id, None)
                if chain_info is None:
                    chain_shortname = get_chain_info(self.db, mch_inlet_info[-2])
                    if not chain_shortname:
                        chain_shortname = ''
                    # has_risk = self.db.selectSQL(risk_sql, (cs_id, 'chain'))[0]
                    chain_info = {
                        'chain_shortname': chain_shortname,
                        # 'has_risk': has_risk
                    }
                    chain_map[cs_id] = chain_info
                mch_inlet_info.insert(-2, chain_info.get('chain_shortname', ''))
                # mch_inlet_info.insert(-2, chain_info.get('has_risk', ''))
                mch_inlet_info.insert(-2, has_risk)
                ret_list.append(tuple(mch_inlet_info))
            return ret_list, ret_list[0][-1]  # 数据,总数
        return ret, 0

    def auth_userid(self, mch_id):
        # selSql = """select bk_user.bk_id,auth_user,mch_id
        #             from auth_mch_info as a1 INNER JOIN  bk_user on bk_user.email=a1.auth_user
        #             where mch_id=%s and not exists(select 1 from auth_mch_info as a2
        #                 where a2.mch_id= a1.mch_id and a2.create_at > a1.create_at);"""
        # db_ret = self.db.selectSQL(selSql, (mch_id,))
        # if db_ret:
        #     return db_ret
        auth_mch_info = uline_session.query(AuthMchInfo).filter(AuthMchInfo.mch_id == mch_id).order_by(
            desc(AuthMchInfo.create_at)).first()
        if auth_mch_info:
            email = auth_mch_info.auth_user
            sys_type_id = self.session["sys_type_id"]
            last_employee = uline_session.query(Employee).join(UserProfile, UserProfile.id == Employee.user_id). \
                filter(UserProfile.email == email, Employee.sys_type_id == sys_type_id).all()
            if last_employee:
                ids = [employee.id for employee in last_employee]
                return ids
            else:
                return []
        else:
            return []
