# -*- coding: utf-8 -*-
'''
BEGIN
添加商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
import os
from tornado import gen
from uline.public import log
from uline.public import common
from uline.handlers.baseHandlers import ChainAdminHandler
from tornado.web import authenticated, HTTPError, asynchronous
from .form import ModifyMerchantlnlet
from uline.public.common import create_or_update_merchant
from uline.public.constants import old_payment_relations
from uline.utils.record import record_utils
from requests_toolbelt.multipart.encoder import MultipartEncoder
from uline.settings import FEATURE_SWITCH
from uline.utils.chain import chain_utils
from uline.model.uline.base import uline_session
from uline.model.uline.user import DtUser
from uline.model.uline.info import DtInletInfo, DtPayment
from uline.public.permit import check_permission


class ModifyCsInletHandler(ChainAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        self.open_wx_app_pay = FEATURE_SWITCH.get('APP_PAY', False)
        self.form = ModifyMerchantlnlet(self)
        self.dt_id = chain_utils.get_dt_id_for_chain_id(self.current_user)
        self.cs_id = self.current_user

        self.bank_no = self.form.bank_no.data
        if self.bank_no:
            bankName = self.get_bank_name()
            setattr(self.form, 'bankName', bankName)
        self.mch_id = self.form.mch_id.data
        db_mch_info = self.get_mch_infos()
        query_industry_no = self.form.industry_no.data

        if not query_industry_no and db_mch_info:
            jobType = db_mch_info[0]
            setattr(self.form.industry_no, 'data', jobType)
        self.industry_no = self.form.industry_no.data

        if self.industry_no and db_mch_info:
            self.industry_name = db_mch_info[2]
            setattr(self.form, 'industryName', self.industry_name)
            area, cmbProvince, cmbCity, cmbArea = (
                self.industry_name).split('-')
            self.form.area.data = area
            self.form.cmbProvince.data = cmbProvince
            self.form.cmbCity.data = cmbCity
            self.form.cmbArea.data = cmbArea

        query_mch_name = self.form.mch_name.data
        if not query_mch_name and db_mch_info:
            self.form.mch_name.data = db_mch_info[1]

        lincense_img = self.get_license_img()
        setattr(self.form.licenseImgOld, 'data', lincense_img)
        # 用于记录当前角色的上级是谁，方便通用接口
        setattr(self.form, 'father_name', 'chain')
        self.has_been_authed = self.has_authed()

        self.dt_user = uline_session.query(DtUser).filter(DtUser.dt_id == self.dt_id)
        self.dt_inlet_info = uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == self.dt_id)
        self.payments_field = {}
        # TODO(leiyutian) 前端传递连锁商户id, 前端通过查询设置表单中的支付方式
        if not self.cs_id:
            self.form.errors['cs_id'] = [u'无有效连锁商户']
        else:
            self.chain_general = uline_session.query(DtUser).filter(DtUser.dt_id == self.cs_id).first()
            if not self.chain_general:
                self.form.errors['cs_id'] = [u'无效的连锁商户']
            else:
                self.payments = uline_session.query(DtPayment).filter(DtPayment.dt_id == self.cs_id).all()
                for each_payment in self.payments:
                    paytype = each_payment.payment_type
                    pay_form = getattr(self.form, 'payment_type' + str(paytype))
                    setattr(pay_form, 'data', each_payment.payment_rate / 10.0)
                    self.payments_field['payment_type' + str(paytype)] = str(each_payment.payment_rate)

    def has_authed(self):
        query = """select 1 from auth_mch_info where mch_id=%s and auth_status=2;"""
        result = self.db.selectSQL(query, (self.mch_id,))
        return bool(result)

    def get_mch_infos(self):
        query = """select mch_inlet_info.u_ind_code, mch_inlet_info.mch_name,industry_uline_info.industry_name
                from mch_inlet_info
                INNER JOIN industry_uline_info ON mch_inlet_info.u_ind_code=industry_uline_info.industry_code
                where mch_inlet_info.mch_id=%s"""
        result = self.db.selectSQL(query, (self.mch_id,))
        return result

    @gen.coroutine
    def get(self):
        wx_channel_id = ""
        with self.db.get_db() as cur:
            dt_user = yield self.get_dt_user(cur)
            wx_sub_mch_id, wx_app_sub_mch_id, rate = dt_user[1], dt_user[2], dt_user[3]
            wx_channel_id = self.get_wx_channel_id(cur)
            can_use_wx_app = self.get_wx_app_payment_rate(cur)
            # 有3个字段经常出现特殊字符，暂时先后台直接给出，不需要前端拼接url
            address, id_card_no, license_scope = self.get_mch_license_scope_and_address(
                cur)
            self.form.address.data = address
            self.form.id_card_no.data = id_card_no
            self.form.license_scope.data = license_scope
        error_inlet_info_html = self.render_string(
            'common/error_inlet_add_info.html', data=self.form)
        self.render(
            'chain/inlet/csModify.html',
            form=self.form,
            has_been_authed=self.has_been_authed,
            error_inlet_info_html=error_inlet_info_html,
            open_wx_app_pay=self.open_wx_app_pay and can_use_wx_app,
            OPEN_D0=self.open_d0,
            wx_channel_id=wx_channel_id
        )

    @asynchronous
    @gen.coroutine
    def post(self):
        setattr(self.form, 'dt_id', self.dt_id)
        setattr(self.form, 'cs_id', self.cs_id)
        with self.db.get_db() as cur:
            dt_user = yield self.get_dt_user(cur)
            wx_sub_mch_id, wx_app_sub_mch_id, rate = dt_user[1], dt_user[2], dt_user[3]

        if self.request.files.get('id_card_img_f'):
            self.form.id_card_img_f.raw_data = self.request.files[
                'id_card_img_f']
        if self.request.files.get('id_card_img_b'):
            self.form.id_card_img_b.raw_data = self.request.files[
                'id_card_img_b']
        if self.request.files.get('license_img'):
            self.form.license_img.raw_data = self.request.files[
                'license_img']

        fields = {}
        for key, value in self.request.arguments.items():
            if key.startswith('payment_type'):
                fields[key] = str(int(float(value[0]) * 10)
                                  ) if value[0] else value[0]
            else:
                fields[key] = value[0]

        # 营业执照是否长期(不传表示非长期)
        if fields.get('license_period'):
            fields['license_period'] = '2'
        else:
            fields['license_period'] = ''
        if fields.get('license_period') == '2':
            fields['license_end_date'] = None

        files = {}

        if self.request.files.get('id_card_img_f'):
            files['id_card_img_f'] = ('id_card_img_f.jpg',
                                      self.form.id_card_img_f.raw_data[0].get(
                                          'body'),
                                      self.form.id_card_img_f.raw_data[0].get('content_type'))

        if self.request.files.get('id_card_img_b'):
            files['id_card_img_b'] = ('id_card_img_b.jpg',
                                      self.form.id_card_img_b.raw_data[0].get(
                                          'body'),
                                      self.form.id_card_img_b.raw_data[0].get('content_type'))

        if self.request.files.get('license_img'):
            files['license_img'] = ('license_img.jpg',
                                    self.form.license_img.raw_data[0].get(
                                        'body'),
                                    self.form.license_img.raw_data[0].get('content_type'))

        fields['father_name'] = getattr(self.form, 'father_name')
        # paymnent转换成uline_paymnet_code
        new_payments = {}
        for payment, value in self.payments_field.iteritems():
            new_payments[old_payment_relations.get(payment[12:])] = value
        fields.update(new_payments)
        fields.update(files)

        multipart_data = MultipartEncoder(fields=fields)

        method = 'POST'
        path = '/v1/mchinlet/update'
        API_ID = str(self.cs_id)
        API_KEY = self.get_chain_api_key()
        response_body = yield create_or_update_merchant(method, path, API_ID, API_KEY, multipart_data)
        if response_body.get('code') == 200:
            self.redirect('/chain/inlet/cs')
            return
        else:
            self.form.errors.update(response_body.get('content', {}))
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(
                'chain/inlet/csModify.html',
                form=self.form,
                OPEN_D0=self.open_d0,
                has_been_authed=self.has_been_authed,
                error_inlet_info_html=error_inlet_info_html,
                open_wx_app_pay=self.open_wx_app_pay and self.get_wx_app_payment_rate(
                    cur)
            )

    def get_bank_name(self):
        query = """select bank_name from balance_bank_info where bank_no=%s;"""
        ret = self.db.selectSQL(query, (self.bank_no, ))
        bank_name = ret[0] if ret else ''
        return bank_name

    def get_job_type(self):
        query = 'select u_ind_code from mch_inlet_info where mch_id=%s;'
        ret = self.db.selectSQL(query, (self.mch_id, ))
        jobType = str(ret[0]) if ret else ''
        return jobType

    def get_license_img(self):
        query = 'select license_img from mch_inlet_info where mch_id=%s;'
        ret = self.db.selectSQL(query, (self.mch_id, ))
        img = str(ret[0]) if ret else ''
        base_dir = '/static/uploads/mch/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
        return os.path.join(file_dir, img)

    def get_license_scope(self):
        query = 'select license_scope from mch_inlet_info where mch_id=%s;'
        ret = self.db.selectSQL(query, (self.mch_id, ))
        scope = ret[0] if ret else ''
        return scope

    @gen.coroutine
    def get_dt_user(self, cursor):
        query = """select
        dt_name, wx_sub_mch_id,
        wx_app_sub_mch_id, rate from dt_user where dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def get_dt_user_wx_appid(self, cursor):
        query = """select wx_sub_mch_id from dt_user where dt_id=%s"""
        cursor.execute(query, (self.dt_id, ))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    def get_chain_api_key(self):
        query = """select api_key from dt_user where dt_id=%s"""
        api_key = self.db.selectSQL(query, (self.cs_id, ))[0]
        if not api_key:
            api_key = common.gen_randown_mch_pkey(32)
            query = """update dt_user set api_key=%s where dt_id=%s;"""
            self.db.executeSQL(query, (api_key, self.cs_id))
        return api_key

    def get_wx_app_payment_rate(self, cursor):
        query = """select 1 from dt_payment where dt_id=%s AND payment_type=4 AND activated_status!=1"""
        cursor.execute(query, (self.cs_id,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_wx_channel_id(self, cursor):
        query = """select wx_channel_id from dt_inlet_info where dt_id=%s"""
        cursor.execute(query, (self.dt_id,))
        ret = cursor.fetchone()
        channel_id = ""
        if ret:
            channel_id_in_db = ret[0]
            channel_id = channel_id_in_db if channel_id_in_db else ""
        return channel_id

    def get_mch_license_scope_and_address(self, cursor):
        query = """select mch_inlet_info.address, mch_balance.id_card_no, mch_inlet_info.license_scope
                  from mch_inlet_info INNER JOIN mch_balance on mch_inlet_info.mch_id = mch_balance.mch_id
                  WHERE mch_inlet_info.mch_id=%s;
        """
        cursor.execute(query, (self.mch_id,))
        ret = cursor.fetchone()
        return ret[0], ret[1], ret[2]
