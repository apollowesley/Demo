# -*- coding: utf-8 -*-
'''
BEGIN
ajax请求 审核/驳回商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import json
from multiprocessing import cpu_count

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.web import asynchronous, authenticated
import tcelery
from celery import chain
from tornado.concurrent import run_on_executor

from uline.backend.tasks import callback_for_mch_auth_result
from uline.handlers.baseHandlers import BkAdminHandler
from uline.public import common
from uline.public import constants
from uline.settings import FEATURE_SWITCH, AUTH_URL
from .form import AuthMerchantInfo
from uline.public.auth_util import MchAuthUtil
from uline.model.uline.user import Employee
from uline.model.uline.info import UserProfile
from uline.model.uline.base import uline_session
from uline.backend.tasks import auth_mch_celery
from concurrent.futures import ThreadPoolExecutor
from uline.public.permit import check_permission

tcelery.setup_nonblocking_producer()
thread_num = cpu_count()


class AuthMerchantInletStatusHandler(BkAdminHandler):
    executor = ThreadPoolExecutor(thread_num)

    @authenticated
    @check_permission
    @gen.coroutine
    def prepare(self):
        self.form = AuthMerchantInfo(self)
        if not self.form.validate():
            f_rsp = common.f_rsp(code=406, msg='fail')
            self.finish(f_rsp)
        self.mch_id = self.form.mch_id.data
        # d0_status = self.db.selectSQL("""
        #     select 1 from mch_payment where payment_type > 100 and mch_id = %s;
        # """, (self.mch_id,))
        # if d0_status:
        #     # TODO 只有这个商户能激活，测试一下D0，后期去掉这些
        #     if str(self.mch_id) not in ['100015251037', '100015666075', '100015664641']:
        #         self.rsp = common.f_rsp(code=411, msg=u'D0功能正在内测阶段，即将开放')
        #         self.finish(self.rsp)
        #         return
        self.create_at = self.update_at = common.timestamp_now()

        self.open_review = FEATURE_SWITCH['REVIEW']
        self.wx_channel_id = None
        self.wx_app_channel_id = None
        if self.open_review:
            self.bk_email = self.auth_user_email(self.session.get('bk_id'))
            # 最近一次审核状态验证,初始化审核状态,和返回码
            with self.db.get_db() as cur:
                ret = self.latest_status(cur)
                self.query_status, self.query_user = ret[0], ret[1]
                if self.query_status == 1:
                    self.status = 4
                    self.rsp = common.scc_rsp(code=200, msg='fsuccess')
                    self.auth_mch_inlet(cur)
                    self.add_auth_inlet_info(cur)
                    self.finish(self.rsp)
                elif self.query_status == 4:
                    self.status = 2
                    self.rsp = common.scc_rsp(code=200, msg='csuccess')
                    if self.query_user == self.bk_email:
                        self.rsp = common.f_rsp(code=406, msg='fail')
                        self.finish(self.rsp)
                elif self.query_status != constants.AUTH_STATUS_INTERNET_FAIL:
                    self.rsp = common.f_rsp(code=406, msg='fail')
                    self.finish(self.rsp)
        else:
            self.status = 2
            self.rsp = common.scc_rsp(code=200, msg='success')

        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER')

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def get(self):
        operate_user = yield self.get_bk_email()
        http_client = AsyncHTTPClient()
        url = AUTH_URL + '/v1/mchauth'
        data = {'mch_id': self.mch_id, 'bk_id': self.current_user, 'operate_user': operate_user}
        response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
        if response.body == '1':
            # fail
            self.rsp = common.f_rsp(code=406, msg='fail')
        else:
            # success
            self.rsp = common.scc_rsp(code=200, msg='inleting')

        # mch_auth_util = MchAuthUtil(self.uline_session, self.current_user, self.mch_id, open_dine=self.open_dine)
        # self.rsp = mch_auth_util.start_auth()
        # if self.rsp.get('code', 406) == 200:
        #     chain_task = chain(auth_mch_celery.s(self.current_user, self.mch_id),
        #                        callback_for_mch_auth_result.s(self.mch_id))
        #     chain_task.apply_async()

        self.write(self.rsp)
        self.finish()

    def auth_user_email(self, bk_id):
        selSql = """select email from bk_user where bk_id=%s"""
        db_ret = self.db.selectSQL(selSql, (bk_id,))
        if db_ret:
            return db_ret[0]

    def latest_status(self, cursor):
        query = """
            SELECT auth_status, auth_user
            from auth_mch_info where mch_id = %s
             order by create_at desc
             LIMIT 1;"""
        cursor.execute(query, (self.mch_id,))
        ret = cursor.fetchone()
        return ret

    @gen.coroutine
    def auth_mch_inlet(self, cursor):
        query = """update mch_inlet_info set
                auth_status=%(auth_status)s,
                update_at=%(update_at)s where mch_id=%(mch_id)s"""
        cursor.execute(query, {
            'auth_status': self.status,
            'update_at': self.update_at,
            'mch_id': self.mch_id
        })

    @gen.coroutine
    def add_auth_inlet_info(self, cursor):
        auth_user = yield self.get_bk_email()
        query = """
                insert into auth_mch_info (
                mch_id, comment, auth_user, auth_status, create_at)
                values (%s, %s, %s, %s, %s);"""
        cursor.execute(
            query,
            (
                self.mch_id,
                constants.AUTH_STATUS[str(self.status)],
                auth_user,
                self.status,
                self.create_at
            )
        )

    @gen.coroutine
    def get_bk_email(self):
        employee_id = self.session["employee_id"]
        employee = uline_session.query(Employee).filter(Employee.id == employee_id).one()
        user_profile = uline_session.query(UserProfile).filter(UserProfile.id == employee.user_id).one()
        email = user_profile.email
        raise gen.Return(email)

        # query = """select email from bk_user where bk_id=%s"""
        # cursor.execute(query, (self.current_user,))
        # ret = cursor.fetchone()
        # raise gen.Return(ret[0])
