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
from __future__ import division
import os
from decimal import Decimal
from requests_toolbelt.multipart.encoder import MultipartEncoder
from tornado import gen
from tornado.web import authenticated, asynchronous

from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import common
from uline.public.common import create_or_update_merchant
from uline.public.constants import AVAILABLE_PAYMENTS, PAY_TYPES, old_payment_relations
from uline.public.constants import new_payment_relations
from uline.settings import FEATURE_SWITCH, MIN_ALI_LEVEL
from .form import ModifyMerchantlnlet
from uline.utils.dayzero import payment_util
from uline.public.permit import check_permission


class ModifyMerchantInletHandler(DtAdminHandler):

    @authenticated
    @check_permission
    def prepare(self):
        self.d0_change = FEATURE_SWITCH.get('DO_CHANGE', False)
        self.h5 = FEATURE_SWITCH.get('H5')
        self.jd_pay = FEATURE_SWITCH.get('JD_PAY')
        self.open_d0 = FEATURE_SWITCH.get('OPEN_D0')
        self.open_wx_app_pay = FEATURE_SWITCH.get('APP_PAY', False)
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

        setattr(self.form, 'dt_id', self.current_user)
        # 用于记录当前角色的上级是谁，方便通用接口
        setattr(self.form, 'father_name', 'dt')
        # 渠道商是否开通D0微信支付
        self.D0_wx = payment_util.get_dt_support_payment_type(
            self.db, 'D0_wx', self.current_user)
        # 渠道商是否开通D0支付宝支付
        self.D0_ali = payment_util.get_dt_support_payment_type(
            self.db, 'D0_alipay', self.current_user)
        rate_status = {
            "D0_wx": str(self.D0_wx).lower(),
            "D0_alipay": str(self.D0_ali).lower()
        }
        setattr(self.form, "rate_status", rate_status)

        self.has_dine = bool(self.dt_has_dine())
        self.open_dine = FEATURE_SWITCH.get('DINE_TOGETHER') and self.has_dine
        self.use_dine = True if self.form.use_dine.data else False

        extension_infos = self.get_extensions()
        for each_name in extension_infos:
            form_key = getattr(self.form, each_name + '_old', None)
            if form_key:
                setattr(form_key, 'data', extension_infos[each_name])
        # 将老的paymnt_type:1,2,3,4 转换成新的 uline_payment_code
        for payment_type in PAY_TYPES:
            payment_rate = self.form.data.get('payment_type' + str(payment_type))
            if payment_rate >= 0:
                setattr(self.form, old_payment_relations.get(str(payment_type)), payment_rate)

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

    def generate_unchanged_render_params(self):
        return {
            'd0_change': self.d0_change,
            'need_m3': MIN_ALI_LEVEL.upper() >= 'M3',
        }

    @gen.coroutine
    def get(self):
        wx_channel_id = ""
        self.use_dine = False
        with self.db.get_db() as cur:
            # dt_user = yield self.get_dt_user(cur)
            # wx_sub_mch_id, wx_app_sub_mch_id, rate = dt_user[1], dt_user[2], dt_user[3]
            wx_channel_id = self.get_wx_channel_id(cur)
            can_use_wx_app = self.get_wx_app_payment_rate(cur)
            can_use_unionpay = self.get_unionpay_payment_rate(cur)
            can_use_wx_h5 = self.get_wx_h5_payment_rate(cur)
            can_use_jd = self.get_jd_payment_rate(cur)
            # 以下字段经常出现特殊字符，暂时先后台直接给出，不需要前端拼接url
            ret = self.get_mch_license_scope_and_address(cur)
            self.form.mch_name.data = ret.get('mch_name')
            self.form.mch_shortname.data = ret.get('mch_shortname')
            self.form.address.data = ret.get('address')
            self.form.id_card_no.data = ret.get('id_card_no')
            self.form.license_scope.data = ret.get('license_scope')
            self.form.balance_name.data = ret.get('balance_name')
            # if self.has_wx_dine_payments(cur):
            #     self.use_dine = True

        self.add_filed()
        self.get_has_channel()

        error_inlet_info_html = self.render_string(
            'common/error_inlet_add_info.html', data=self.form)
        self.render(
            'distributor/inlet/merchantModify.html',
            h5=self.h5 and can_use_wx_h5,
            form=self.form,
            has_been_authed=self.has_been_authed,
            error_inlet_info_html=error_inlet_info_html,
            open_wx_app_pay=self.open_wx_app_pay and can_use_wx_app,
            OPEN_D0=self.open_d0,
            jd_pay=self.jd_pay,
            can_use_unionpay=can_use_unionpay,
            can_use_jd=can_use_jd,
            wx_channel_id=wx_channel_id
        )

    def add_filed(self):
        # 是否勾选
        keys = ['WX', 'WX_OFFLINE', 'WX_ONLINE', 'WX_DINE', 'WX_ZERO', 'WX_D0', 'WX_D1',
                'ALI', 'ALI_D1', 'ALI_D0', 'ALI_ZERO', 'ALI_OFFLINE', 'JD']
        for key in keys:
            setattr(self.form, key, '')
        for payment_type in AVAILABLE_PAYMENTS.keys():
            payment_rate = getattr(self.form, payment_type).data
            if payment_rate >= 0:
                # 转 paymnet_code
                setattr(self.form, 'payment_type%s' % new_payment_relations.get(payment_type), payment_rate)
                self.validate_rate = True
                # 方便前端显示，添加一些字段
                # 支付通道判断
                if payment_type.startswith('WX'):
                    setattr(self.form, 'WX', True)

                    # 通道判断
                    if payment_type.startswith('WX_OFFLINE'):
                        self.has_wx_offline = True
                        setattr(self.form, 'WX_OFFLINE', True)
                    elif payment_type.startswith('WX_ONLINE'):
                        self.has_wx_online = True
                        setattr(self.form, 'WX_ONLINE', True)
                    elif payment_type.startswith('WX_DINE'):
                        setattr(self.form, 'WX_DINE', True)
                        self.use_dine = True
                    elif payment_type.startswith('WX_ZERO'):
                        setattr(self.form, 'WX_ZERO', True)

                    # 结算方式判断
                    if payment_type.endswith('D0'):
                        self.has_wx_d0 = True
                        setattr(self.form, 'WX_D0', True)
                    else:
                        setattr(self.form, 'WX_D1', True)
                elif payment_type.startswith('ALI'):
                    setattr(self.form, 'ALI', True)
                    if payment_type.startswith('ALI_OFFLINE'):
                        setattr(self.form, 'ALI_OFFLINE', True)
                    elif payment_type.startswith('ALI_ZERO'):
                        setattr(self.form, 'ALI_ZERO', True)
                    if payment_type.endswith('D0'):
                        self.has_ali_d0 = True
                        setattr(self.form, 'ALI_D0', True)
                    else:
                        setattr(self.form, 'ALI_D1', True)
                elif payment_type.startswith('JD'):
                    setattr(self.form, 'JD', True)

        if self.form.wx_draw_fee.data is not None or self.form.wx_draw_rate.data is not None:
            self.has_wx_d0 = True
            setattr(self.form, 'WX_D0', True)
        if self.form.ali_draw_fee.data is not None or self.form.ali_draw_rate.data is not None:
            self.has_ali_d0 = True
            setattr(self.form, 'ALI_D0', True)

    def get_has_channel(self):
        # 是否显示
        keys = ['HAS_WX', 'HAS_WX_OFFLINE', 'HAS_WX_ONLINE', 'HAS_WX_DINE', 'HAS_WX_ZERO', 'HAS_WX_D0', 'HAS_WX_D1',
                'HAS_ALI', 'HAS_ALI_D1', 'HAS_ALI_D0', 'HAS_ALI_ZERO', 'HAS_ALI_OFFLINE']
        for key in keys:
            setattr(self.form, key, '')

        sql = """select uline_payment_code, uline_settle_id from dt_payment where dt_id=%s"""
        ret = self.db.selectSQL(sql, (self.current_user,), fetchone=False)
        for single_paymnet in ret:
            payment_type = single_paymnet[0]
            uline_settle_id = single_paymnet[1]
            if uline_settle_id == 2:
                payment_type += '_D0'
            if payment_type.startswith('WX'):
                setattr(self.form, 'HAS_WX', True)

                # 通道判断
                if payment_type.startswith('WX_OFFLINE'):
                    self.has_wx_offline = True
                    setattr(self.form, 'HAS_WX_OFFLINE', True)
                elif payment_type.startswith('WX_ONLINE'):
                    self.has_wx_online = True
                    setattr(self.form, 'HAS_WX_ONLINE', True)
                elif payment_type.startswith('WX_DINE'):
                    setattr(self.form, 'HAS_WX_DINE', True)
                elif payment_type.startswith('WX_ZERO'):
                    setattr(self.form, 'HAS_WX_ZERO', True)
                # 结算方式判断
                if payment_type.endswith('D0'):
                    self.has_wx_d0 = True
                    setattr(self.form, 'HAS_WX_D0', True)
                else:
                    setattr(self.form, 'HAS_WX_D1', True)

            elif payment_type.startswith('ALI'):
                setattr(self.form, 'HAS_ALI', True)
                if payment_type.startswith('ALI_OFFLINE'):
                    setattr(self.form, 'HAS_ALI_OFFLINE', True)
                elif payment_type.startswith('ALI_ZERO'):
                    setattr(self.form, 'HAS_ALI_ZERO', True)
                if payment_type.endswith('D0'):
                    self.has_ali_d0 = True
                    setattr(self.form, 'HAS_ALI_D0', True)
                else:
                    setattr(self.form, 'HAS_ALI_D1', True)

        with self.db.get_db() as cur:
            dt_draw_fee_wx = self.get_dt_draw_fee_wx(cur)
            if dt_draw_fee_wx:
                self.has_wx_d0 = True
                setattr(self.form, 'HAS_WX_D0', True)
            dt_draw_fee_ali = self.get_dt_draw_fee_ali(cur)
            if dt_draw_fee_ali:
                self.has_ali_d0 = True
                setattr(self.form, 'HAS_ALI_D0', True)

    @asynchronous
    @gen.coroutine
    def post(self):
        setattr(self.form, 'dt_id', self.current_user)
        with self.db.get_db() as cur:
            # dt_user = yield self.get_dt_user(cur)
            can_use_jd = self.get_jd_payment_rate(cur)
            can_use_unionpay = self.get_unionpay_payment_rate(cur)
            # wx_sub_mch_id, wx_app_sub_mch_id, rate = dt_user[1], dt_user[2], dt_user[3]

        if self.request.files.get('id_card_img_f'):
            self.form.id_card_img_f.raw_data = self.request.files['id_card_img_f']
        if self.request.files.get('id_card_img_b'):
            self.form.id_card_img_b.raw_data = self.request.files['id_card_img_b']
        if self.request.files.get('license_img'):
            self.form.license_img.raw_data = self.request.files['license_img']
        if self.request.files.get('img_with_id_card'):
            self.form.img_with_id_card.raw_data = self.request.files.get(
                'img_with_id_card', None)

        # 进件补充材料
        self.form.annex_img1.raw_data = self.request.files.get('annex_img1', None)
        self.form.annex_img2.raw_data = self.request.files.get('annex_img2', None)
        self.form.annex_img3.raw_data = self.request.files.get('annex_img3', None)
        self.form.annex_img4.raw_data = self.request.files.get('annex_img4', None)
        self.form.annex_img5.raw_data = self.request.files.get('annex_img5', None)

        # 提现手续费
        self.wx_draw_fee = self.ali_draw_fee = None
        if self.form.wx_draw_fee.data:
            self.wx_draw_fee = self.form.wx_draw_fee.data
        elif self.form.wx.data:
            self.wx_draw_fee = self.form.wx.data
        if self.form.ali_draw_fee.data:
            self.ali_draw_fee = self.form.ali_draw_fee.data
        elif self.form.alipay.data:
            self.ali_draw_fee = self.form.alipay.data
        # 提现垫资费
        self.wx_draw_rate = self.form.wx_draw_rate.data
        self.ali_draw_rate = self.form.ali_draw_rate.data

        # 新版的手续费和垫资费，两个都为空或者两个都不为空
        if FEATURE_SWITCH.get('NEW_INLET'):
            if (self.wx_draw_fee and not self.wx_draw_rate) or (not self.wx_draw_fee and self.wx_draw_rate):
                self.form.errors['wx_draw_fee'] = [u'微信D0垫资费率不能只填一项']
            if (self.ali_draw_fee and not self.ali_draw_rate) or (not self.ali_draw_fee and self.ali_draw_rate):
                self.form.errors['ali_draw_fee'] = [u'支付宝D0垫资费率不能只填一项']

        self.add_filed()
        self.get_has_channel()

        # 围餐补充材料
        for index in range(1, 6):
            img_key = 'wx_dine_annex_img' + str(index)
            setattr(getattr(self.form, img_key), 'raw_data', self.request.files.get(img_key, None))

        if self.use_dine and self.open_dine:
            self.form.mch_desk_img.raw_data = self.request.files.get(
                'mch_desk_img', None)
            self.form.mch_inner_img.raw_data = self.request.files.get(
                'mch_inner_img', None)
            self.form.mch_front_img.raw_data = self.request.files.get(
                'mch_front_img', None)
            if self.form.mch_desk_img.raw_data is None or self.form.mch_desk_img.raw_data[0] is None:
                self.form.errors['mch_desk_img'] = [u'必须传入商户收银台照片']
            if self.form.mch_inner_img.raw_data is None or self.form.mch_inner_img.raw_data[0] is None:
                self.form.errors['mch_inner_img'] = [u'必须传入商户内部环境照片']
            if self.form.mch_front_img.raw_data is None or self.form.mch_front_img.raw_data[0] is None:
                self.form.errors['mch_front_img'] = [u'必须传入商户门口照片']
            if self.form.errors:
                error_inlet_info_html = self.render_string(
                    'common/error_inlet_add_info.html', data=self.form)
                self.render(
                    'distributor/inlet/merchantModify.html',
                    h5=self.h5 and self.get_wx_h5_payment_rate(cur),
                    form=self.form,
                    OPEN_D0=self.open_d0,
                    has_been_authed=self.has_been_authed,
                    error_inlet_info_html=error_inlet_info_html,
                    jd_pay=self.jd_pay,
                    can_use_jd=can_use_jd,
                    open_wx_app_pay=self.open_wx_app_pay and self.get_wx_app_payment_rate(cur)
                )
                return

        fields = {}
        for key, value in self.request.arguments.items():
            if key.startswith('payment_type') or key in AVAILABLE_PAYMENTS.keys() or \
                    key in ['wx_draw_rate', 'ali_draw_rate']:
                _rate = value[0].replace(" ", "")
                try:
                    last_rate = str(int(float(_rate) * 10)) if _rate else _rate
                except Exception:
                    self.form.errors['payment_type1'] = [u'无效的费率']
                    error_inlet_info_html = self.render_string(
                        'common/error_inlet_add_info.html', data=self.form)
                    self.render(
                        'distributor/inlet/merchantModify.html',
                        h5=self.h5 and self.get_wx_h5_payment_rate(cur),
                        form=self.form,
                        OPEN_D0=self.open_d0,
                        has_been_authed=self.has_been_authed,
                        error_inlet_info_html=error_inlet_info_html,
                        jd_pay=self.jd_pay,
                        can_use_jd=can_use_jd,
                        open_wx_app_pay=self.open_wx_app_pay and self.get_wx_app_payment_rate(cur)
                    )
                    return
                # if key in AVAILABLE_PAYMENTS.keys():
                #     fields['payment_type' + str(new_payment_relations.get(key))] = last_rate
                # else:
                fields[key] = last_rate
            # elif key in ['province', 'city']:
            #     fields[key] = value[0].split('-')[1]
            else:
                fields[key] = value[0]
                if key in ['wx', 'alipay', 'wx_draw_fee', 'ali_draw_fee']:
                    _rate = value[0].replace(" ", "")
                    fields[key] = str(int((Decimal(_rate) * 100))) if _rate else _rate

        # 营业执照是否长期(不传表示非长期)
        if fields.get('license_period'):
            fields['license_period'] = '2'
        else:
            fields['license_period'] = ''
        if fields.get('license_period') == '2':
            fields['license_end_date'] = None
        if self.use_dine:
            fields['use_dine'] = '1'

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
        if self.request.files.get('img_with_id_card'):
            files['img_with_id_card'] = ('img_with_id_card.jpg',
                                         self.form.img_with_id_card.raw_data[0].get(
                                             'body'),
                                         self.form.img_with_id_card.raw_data[0].get('content_type'))

        # 围餐商户照片
        desk_file_data = self.request.files.get('mch_desk_img', None)
        if desk_file_data:
            files['mch_desk_img'] = ('mch_desk_img.jpg',
                                     desk_file_data[0].get('body'),
                                     desk_file_data[0].get('content_type'))
            self.form.mch_desk_img.raw_data = desk_file_data
            self.form.mch_desk_img.raw_data = desk_file_data

        # 进件补充材料
        for img_count in range(1, 6):
            img_name = 'annex_img' + str(img_count)
            annex_img_data = getattr(self.form, img_name).raw_data
            # 如果不为None
            if annex_img_data:
                files.update({
                    img_name: (
                        img_name + '.jpg',
                        annex_img_data[0].get('body'),
                        annex_img_data[0].get('content_type')
                    ),
                })

        # 围餐补充材料
        for img_index in range(1, 6):
            img_key = 'wx_dine_annex_img' + str(img_index)
            files.update(self.get_file_infos(img_key))

        inner_file_data = self.request.files.get('mch_inner_img', None)
        if self.request.files.get('mch_inner_img', None):
            files['mch_inner_img'] = ('mch_inner_img.jpg',
                                      inner_file_data[0].get('body'),
                                      inner_file_data[0].get('content_type'))
            self.form.mch_inner_img.raw_data = inner_file_data

        front_file_data = self.request.files.get('mch_front_img', None)
        if self.request.files.get('mch_front_img', None):
            files['mch_front_img'] = ('mch_front_img.jpg',
                                      front_file_data[0].get('body'),
                                      front_file_data[0].get('content_type'))
            self.form.mch_front_img.raw_data = front_file_data

        fields['father_name'] = getattr(self.form, 'father_name')
        fields.update(files)

        multipart_data = MultipartEncoder(fields=fields)

        method = 'POST'
        path = '/v1/mchinlet/update'
        API_ID = str(self.current_user)
        API_KEY = self.get_dt_api_key()
        response_body = yield create_or_update_merchant(method, path, API_ID, API_KEY, multipart_data)
        if response_body.get('code') == 200:
            self.redirect('/dist/inlet/mch')
            return
        else:
            self.form.errors.update(response_body.get('content', {}))
            error_inlet_info_html = self.render_string(
                'common/error_inlet_add_info.html', data=self.form)
            self.render(
                'distributor/inlet/merchantModify.html',
                h5=self.h5 and self.get_wx_h5_payment_rate(cur),
                form=self.form,
                OPEN_D0=self.open_d0,
                has_been_authed=self.has_been_authed,
                error_inlet_info_html=error_inlet_info_html,
                jd_pay=self.jd_pay,
                can_use_jd=can_use_jd,
                can_use_unionpay=can_use_unionpay,
                open_wx_app_pay=self.open_wx_app_pay and self.get_wx_app_payment_rate(cur)
            )

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
        query = """select 1 from dt_payment where dt_id=%s AND payment_type in (4,104)"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_unionpay_payment_rate(self, cursor):
        # query = """select 1 from dt_payment where dt_id=%s AND payment_type=4 AND activated_status!=1"""
        query = """select 1 from dt_payment where dt_id=%s AND payment_type in (33)"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_wx_h5_payment_rate(self, cursor):
        query = """select 1 from dt_payment where dt_id=%s AND payment_type in (5,105)"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_jd_payment_rate(self, cursor):
        query = """select 1 from dt_payment where dt_id=%s AND payment_type in (21, 22, 23)"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_dt_draw_fee_wx(self, cursor):
        # 后期改为根据uline_paymnet_code
        query = """select 1 from dt_payment where dt_id=%s AND payment_type in (1,2,3,4,5) AND
                    withdraw_fee is not NULL;"""
        cursor.execute(query, (self.current_user,))
        ret = cursor.fetchone()
        return ret[0] if ret else ''

    def get_dt_draw_fee_ali(self, cursor):
        # 后期改为根据uline_paymnet_code
        query = """select 1 from dt_payment where dt_id=%s AND payment_type in (7,8,9) AND
                    withdraw_fee is not NULL;"""
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

    def get_mch_license_scope_and_address(self, cursor):
        query = """select mch_inlet_info.mch_name, mch_inlet_info.mch_shortname,
                  mch_inlet_info.address, mch_balance.id_card_no, mch_inlet_info.license_scope,
                  mch_balance.balance_name
                  from mch_inlet_info INNER JOIN mch_balance on mch_inlet_info.mch_id = mch_balance.mch_id
                  WHERE mch_inlet_info.mch_id=%s;
        """
        cursor.execute(query, (self.mch_id,))
        ret = cursor.fetchone()
        _field = ['mch_name', 'mch_shortname', 'address',
                  'id_card_no', 'license_scope', 'balance_name']
        return {k: v for k, v in zip(_field, ret)}

    def has_wx_dine_payments(self, cursor):
        query = """select 1 from mch_payment where mch_id=%s and payment_type in (11,12,13)"""
        cursor.execute(query, (self.mch_id,))
        return cursor.fetchone()

    def dt_has_dine(self):
        sql = """select 1 from dt_payment where dt_id=%s and payment_type in (11, 12, 13)"""
        return self.db.selectSQL(sql, (self.current_user,))

    def get_file_infos(self, img_form_name):
        file_info = {}
        img_data = getattr(self.form, img_form_name).raw_data
        # 如果不为None
        if img_data:
            file_info = {
                img_form_name: (img_form_name + '.jpg', img_data[0].get('body'), img_data[0].get('content_type')),
            }
        return file_info

    def get_extensions(self):
        query = 'select extension_name, extension_value from role_info_extension where role_id=%s and role_type=%s;'
        ret = self.db.selectSQL(query, (self.mch_id, 'mch'), fetchone=False, use_dict=True)
        extension_keys = ['mch_front_img', 'mch_inner_img', 'mch_desk_img']
        extension_keys.extend('wx_dine_annex_img' + str(i) for i in range(1, 6))
        extension_infos = dict()
        base_dir = '/static/uploads/mch/idcard'
        file_dir = os.path.join(base_dir, '{}'.format(self.mch_id))
        if ret:
            for extension in ret:
                if extension['extension_value'] and extension['extension_name'] in extension_keys:
                    extension_infos[extension['extension_name']] = os.path.join(
                        file_dir, extension['extension_value'])
        return extension_infos
