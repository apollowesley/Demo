#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @author: leiyutian
# @createTime: 2017-06-01, 17:02:03 GMT+0800
# @description: 添加连锁门店

from __future__ import division

from tornado import gen
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common
from tornado.web import authenticated, asynchronous
from uline.handlers.app.distributor.inlet.form import AddMerchantlnlet
from requests_toolbelt.multipart.encoder import MultipartEncoder
from uline.public.common import create_or_update_merchant
from uline.model.uline.base import uline_session
from uline.public.constants import old_payment_relations
from uline.settings import FEATURE_SWITCH
from uline.model.uline.user import DtUser
from uline.model.uline.info import DtInletInfo, DtPayment
from uline.model.uline.other import AuthDtInfo
from uline.public.permit import check_permission


class AddChainBranchHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.open_wx_app_pay = FEATURE_SWITCH.get('APP_PAY', False)
        self.open_d0 = FEATURE_SWITCH.get('CHAIN_D0')
        self.form = AddMerchantlnlet(self)
        setattr(self.form, 'dt_id', self.current_user)
        # 用于记录当前角色的上级是谁，方便通用接口
        setattr(self.form, 'father_name', 'dt')
        self.dt_user = uline_session.query(DtUser).filter(DtUser.dt_id == self.current_user)
        self.dt_inlet_info = uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == self.current_user)
        self.cs_id = self.form.cs_id.data
        self.form.cs_name = ''
        # TODO(leiyutian) 前端传递连锁商户id, 前端通过查询设置表单中的支付方式
        self.payments_field = {}
        self.payments = uline_session.query(DtPayment).filter(DtPayment.dt_id == self.cs_id).all()
        for each_payment in self.payments:
            paytype = each_payment.payment_type
            pay_form = getattr(self.form, 'payment_type' + str(paytype))
            setattr(pay_form, 'data', each_payment.payment_rate / 10.0)
            self.payments_field['payment_type' + str(paytype)] = str(each_payment.payment_rate)

    @gen.coroutine
    def get(self):
        with self.db.get_db() as cur:
            dt_user = yield self.get_dt_user(cur)
            wx_sub_mch_id, wx_app_sub_mch_id, rate = dt_user[1], dt_user[2], dt_user[3]
            can_use_wx_app = self.get_wx_app_payment_rate(cur)

        self.render(
            'distributor/inlet/csAdd.html',
            form=self.form,
            wx_app=1 if ((wx_sub_mch_id or wx_app_sub_mch_id) and rate != 1) else 0,
            open_wx_app_pay=self.open_wx_app_pay and can_use_wx_app
        )

    def generate_unchanged_render_params(self):
        return {
            'form': self.form,
            'error_inlet_info_html': self.render_string('common/error_inlet_add_info.html', data=self.form),
            'OPEN_D0': self.open_d0,
        }

    @asynchronous
    @gen.coroutine
    def post(self):
        wx_channel_id = ""
        with self.db.get_db() as cur:
            dt_user = yield self.get_dt_user(cur)
            wx_sub_mch_id, wx_app_sub_mch_id, rate = dt_user[1], dt_user[2], dt_user[3]
            wx_channel_id = self.get_wx_channel_id(cur)

        self.u_ind_code = self.form.industry_no.data
        if self.u_ind_code:
            self.industry_name = self.get_industry_name()
            setattr(self.form, 'industryName', self.industry_name)
            area, cmbProvince, cmbCity, cmbArea = (
                self.industry_name).split('-')
            self.form.area.data = area
            self.form.cmbProvince.data = cmbProvince
            self.form.cmbCity.data = cmbCity
            self.form.cmbArea.data = cmbArea
        self.form.cs_name = ''
        if not self.cs_id:
            self.form.errors['cs_id'] = [u'无有效连锁商户']
        else:
            self.chain_general = uline_session.query(DtUser).filter(DtUser.dt_id == self.cs_id).first()
            if not self.chain_general:
                self.form.errors['cs_id'] = [u'无效的连锁商户']
            else:
                auth_success_info = uline_session.query(AuthDtInfo).filter(
                    AuthDtInfo.dt_id == self.current_user, AuthDtInfo.auth_status == 2).first()

                if not auth_success_info:
                    self.form.errors['cs_id'] = [u'连锁商户未通过审核']

                dt_info = uline_session.query(DtUser).filter(DtUser.dt_id == self.cs_id).first()
                if dt_info:
                    self.form.cs_name = dt_info.dt_name

        can_use_wx_app = False
        with self.db.get_db() as cur:
            can_use_wx_app = self.get_wx_app_payment_rate(cur)

        if self.form.errors:
            self.render(
                'distributor/inlet/csAdd.html',
                form=self.form,
                wx_app=1 if ((wx_sub_mch_id or wx_app_sub_mch_id) and rate != 1) else 0,
                open_wx_app_pay=self.open_wx_app_pay and can_use_wx_app
            )
            return

        self.form.id_card_img_f.raw_data = self.request.files.get(
            'id_card_img_f', None)
        self.form.id_card_img_b.raw_data = self.request.files.get(
            'id_card_img_b', None)
        self.form.license_img.raw_data = self.request.files.get(
            'license_img', None)

        bankName = self.get_bank_name() if self.form.bank_no.data else ''
        setattr(self.form, 'bankName', bankName)

        # 判断是否有3张照片
        if (self.form.id_card_img_f.raw_data is None) or (
                self.form.id_card_img_b.raw_data is None) or (
                self.form.license_img.raw_data is None):
            self.form.errors['img'] = [u'必须传入照片']
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(
                'distributor/inlet/csAdd.html',
                form=self.form,
                wx_app=1 if ((wx_sub_mch_id or wx_app_sub_mch_id) and rate != 1) else 0,
                error_inlet_info_html=error_inlet_info_html,
                open_wx_app_pay=wx_channel_id or (
                    self.open_wx_app_pay and wx_app_sub_mch_id)
            )
            return

        # fields = {k:v[0] for k, v in self.request.arguments.items()}
        fields = {}
        for key, value in self.request.arguments.items():
            # if key in ['province', 'city']:
            #     fields[key] = value[0].split('-')[1]
            # else:
            fields[key] = value[0]
        # paymnent转换成uline_paymnet_code
        new_payments = {}
        for payment, value in self.payments_field.iteritems():
            new_payments[old_payment_relations.get(payment[12:])] = value
        fields.update(new_payments)

        # 营业执照是否长期(不传表示非长期)
        if fields.get('license_period'):
            fields['license_period'] = '2'
        else:
            fields['license_period'] = ''
        if fields.get('license_period') == '2':
            fields['license_end_date'] = None
        fields['cs_id'] = str(self.cs_id)

        files = {
            'id_card_img_f': ('id_card_img_f.jpg',
                              self.form.id_card_img_f.raw_data[0].get('body'),
                              self.form.id_card_img_f.raw_data[0].get('content_type')),
            'id_card_img_b': ('id_card_img_b.jpg',
                              self.form.id_card_img_b.raw_data[0].get('body'),
                              self.form.id_card_img_b.raw_data[0].get('content_type')),
            'license_img': ('license_img.jpg',
                            self.form.license_img.raw_data[0].get('body'),
                            self.form.license_img.raw_data[0].get('content_type')),
        }

        fields['father_name'] = getattr(self.form, 'father_name')
        fields.update(files)

        multipart_data = MultipartEncoder(fields=fields)

        method = 'POST'
        path = '/v1/mchinlet'
        API_ID = str(self.current_user)
        API_KEY = self.get_dt_api_key()
        response_body = yield create_or_update_merchant(method, path, API_ID, API_KEY, multipart_data)
        if response_body.get('code') == 200:
            self.redirect('/dist/inlet/cs')
            return
        else:
            self.form.errors.update(response_body.get('content', {}))
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)

            # 用户填错后，可以恢复之前填写的行业类型和结算银行
            self.u_ind_code = self.form.industry_no.data
            if self.u_ind_code:
                self.industry_name = self.get_industry_name()
                setattr(self.form, 'industryName', self.industry_name)
                area, cmbProvince, cmbCity, cmbArea = (
                    self.industry_name).split('-')
                self.form.area.data = area
                self.form.cmbProvince.data = cmbProvince
                self.form.cmbCity.data = cmbCity
                self.form.cmbArea.data = cmbArea

            self.render(
                'distributor/inlet/csAdd.html',
                form=self.form,
                wx_app=1 if ((wx_sub_mch_id or wx_app_sub_mch_id) and rate != 1) else 0,
                error_inlet_info_html=error_inlet_info_html,
                open_wx_app_pay=self.open_wx_app_pay and wx_app_sub_mch_id
            )

    def get_industry_name(self):
        query = """select industry_name from
        industry_uline_info where industry_code=%s;"""
        ret = self.db.selectSQL(query, (self.u_ind_code,))
        industry_name = ret[0] if ret else ''
        return industry_name

    def get_bank_name(self):
        query = """select bank_name from balance_bank_info where bank_no=%s;"""
        ret = self.db.selectSQL(query, (self.form.bank_no.data,))
        bank_name = ret[0] if ret else ''
        return bank_name

    @gen.coroutine
    def get_dt_user(self, cursor):
        query = """select
        dt_name, wx_sub_mch_id,
        wx_app_sub_mch_id, rate from dt_user where dt_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    def get_dt_api_key(self):
        query = """select api_key from dt_user where dt_id=%s"""
        api_key = self.db.selectSQL(query, (self.current_user, ))[0]
        if not api_key:
            api_key = common.gen_randown_mch_pkey(32)
            query = """update dt_user set api_key=%s where dt_id=%s;"""
            self.db.executeSQL(query, (api_key, self.current_user))
        return api_key

    def get_wx_app_payment_rate(self, cursor):
        query = """select 1 from dt_payment where dt_id=%s AND payment_type=4 AND activated_status!=1"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_wx_channel_id(self, cursor):
        query = """select wx_channel_id from dt_inlet_info where dt_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        channel_id = ""
        if ret:
            channel_id_in_db = ret[0]
            channel_id = channel_id_in_db if channel_id_in_db else ""
        return channel_id
