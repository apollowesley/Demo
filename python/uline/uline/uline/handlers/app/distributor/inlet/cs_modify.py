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
from requests_toolbelt.multipart.encoder import MultipartEncoder
from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import DtAdminHandler
from uline.model.uline.base import uline_session
from uline.model.uline.info import DtPayment
from uline.model.uline.other import AuthDtInfo
from uline.model.uline.user import DtUser
from uline.model.uline.info import MchInletInfo
from uline.public import common
from uline.public.common import create_or_update_merchant
from uline.public.constants import old_payment_relations
from uline.settings import FEATURE_SWITCH
from .form import ModifyMerchantlnlet
from uline.public.permit import check_permission


class ModifyCSInletHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        # TODO(leiyutian) 支付方式显示？
        self.open_d0 = FEATURE_SWITCH.get('CHAIN_D0')
        self.form = ModifyMerchantlnlet(self)

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
        setattr(self.form, 'father_name', 'dt')
        self.has_been_authed = self.has_authed()
        self.payments_field = {}
        self.cs_id = self.form.cs_id.data

        self.form.cs_name = ""
        if not self.cs_id:
            mch_info = uline_session.query(MchInletInfo).filter(
                MchInletInfo.mch_id == self.mch_id).first()
            if mch_info:
                self.form.cs_id.data = mch_info.cs_id
                self.cs_id = mch_info.cs_id
                # self.form.cs_name = mch_info.mch_name
        if self.cs_id:
            dt_info = uline_session.query(DtUser).filter(
                DtUser.dt_id == self.cs_id).first()
            if dt_info:
                self.form.cs_name = dt_info.dt_name
        self.payments = uline_session.query(DtPayment).filter(
            DtPayment.dt_id == self.cs_id).all()
        for each_payment in self.payments:
            paytype = each_payment.payment_type
            pay_form = getattr(self.form, 'payment_type' + str(paytype))
            setattr(pay_form, 'data', each_payment.payment_rate / 10.0)
            self.payments_field['payment_type' +
                                str(paytype)] = str(each_payment.payment_rate)

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
        with self.db.get_db() as cur:
            # 有3个字段经常出现特殊字符，暂时先后台直接给出，不需要前端拼接url
            address, id_card_no, license_scope = self.get_mch_license_scope_and_address(
                cur)
            self.form.address.data = address
            self.form.id_card_no.data = id_card_no
            self.form.license_scope.data = license_scope
        self.render('distributor/inlet/csModify.html')

    def generate_unchanged_render_params(self):
        return {
            'form': self.form,
            'has_been_authed': self.has_been_authed,
            'error_inlet_info_html': self.render_string('common/error_inlet_add_info.html', data=self.form),
            'OPEN_D0': self.open_d0,
        }

    @asynchronous
    @gen.coroutine
    def post(self):
        setattr(self.form, 'dt_id', self.current_user)

        # 如果门店没有审核通过过并且有连锁商户id，则需要对数据进行验证
        if self.cs_id and not self.has_been_authed:
            self.chain_general = uline_session.query(
                DtUser).filter(DtUser.dt_id == self.cs_id).first()
            if not self.chain_general:
                self.form.errors['cs_id'] = [u'无效的连锁商户']
            else:
                auth_success_info = uline_session.query(AuthDtInfo).filter(
                    AuthDtInfo.dt_id == self.current_user, AuthDtInfo.auth_status == 2).first()

                if not auth_success_info:
                    self.form.errors['cs_id'] = [u'连锁商户未通过审核']
        if self.form.errors:
            self.render('distributor/inlet/csModify.html')
            return

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
                _rate = value[0].replace(" ", "")
                fields[key] = str(int(float(_rate) * 10)) if _rate else _rate
            else:
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
        fields.update(files)

        multipart_data = MultipartEncoder(fields=fields)

        method = 'POST'
        path = '/v1/mchinlet/update'
        API_ID = str(self.current_user)
        API_KEY = self.get_dt_api_key()
        response_body = yield create_or_update_merchant(method, path, API_ID, API_KEY, multipart_data)
        if response_body.get('code') == 200:
            self.redirect('/dist/inlet/cs')
            return
        else:
            self.form.errors.update(response_body.get('content', {}))
            self.render('distributor/inlet/csModify.html')

    def get_bank_name(self):
        query = """select bank_name from balance_bank_info where bank_no=%s;"""
        ret = self.db.selectSQL(query, (self.bank_no,))
        bank_name = ret[0] if ret else ''
        return bank_name

    def get_job_type(self):
        query = 'select u_ind_code from mch_inlet_info where mch_id=%s;'
        ret = self.db.selectSQL(query, (self.mch_id,))
        jobType = str(ret[0]) if ret else ''
        return jobType

    def get_license_img(self):
        query = 'select license_img from mch_inlet_info where mch_id=%s;'
        ret = self.db.selectSQL(query, (self.mch_id,))
        img = str(ret[0]) if ret else ''
        base_dir = '/static/uploads/mch/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
        return os.path.join(file_dir, img)

    def get_license_scope(self):
        query = 'select license_scope from mch_inlet_info where mch_id=%s;'
        ret = self.db.selectSQL(query, (self.mch_id,))
        scope = ret[0] if ret else ''
        return scope

    @gen.coroutine
    def get_dt_user(self, cursor):
        query = """select
        dt_name, wx_sub_mch_id,
        wx_app_sub_mch_id, rate from dt_user where dt_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        raise gen.Return(ret)

    @gen.coroutine
    def get_dt_user_wx_appid(self, cursor):
        query = """select wx_sub_mch_id from dt_user where dt_id=%s"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        raise gen.Return(ret[0])

    def get_dt_api_key(self):
        query = """select api_key from dt_user where dt_id=%s"""
        api_key = self.db.selectSQL(query, (self.current_user,))[0]
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

    def get_mch_license_scope_and_address(self, cursor):
        query = """select mch_inlet_info.address, mch_balance.id_card_no, mch_inlet_info.license_scope
                  from mch_inlet_info INNER JOIN mch_balance on mch_inlet_info.mch_id = mch_balance.mch_id
                  WHERE mch_inlet_info.mch_id=%s;
        """
        cursor.execute(query, (self.mch_id,))
        ret = cursor.fetchone()
        return ret[0], ret[1], ret[2]
