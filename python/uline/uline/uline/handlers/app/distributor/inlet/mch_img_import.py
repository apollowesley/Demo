# -*- coding: utf-8 -*-
'''
BEGIN
批量导入商户进件信息
    必选参数:

    可选参数:

    成功:
        {"code": 200, "msg": "成功"}
    失败:
        {"code": 406, "msg": "失败"}
END
'''
from __future__ import unicode_literals
import os
from tornado.web import authenticated, asynchronous
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import log
from .form import UploadMerchantInletImage
from uline.public.permit import check_permission


class ImportMerchantImageHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(16)

    @authenticated
    @check_permission
    def prepare(self):
        self.rsp = {'code': 406, 'msg': 'fail'}
        self.form = UploadMerchantInletImage(self)
        self.form.img_file.raw_data = self.request.files['img_file']
        self.uuid = self.form.uuid.data
        file_path = self.is_exist_file_path()

        if not os.path.exists(file_path):
            self.write(self.rsp)
            self.finish()

    def check_xsrf_cookie(self):
        pass

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def post(self):
        if not self.form.validate():
            self.write(self.rsp)
            self.finish()
            return

        imgFile = self.request.files.get('img_file')
        file_path = yield self.create_tmp_image_path(imgFile)
        if not isinstance(file_path, unicode):
            file_path = unicode(file_path, 'utf8')
        try:
            with open(file_path, 'wb') as f:
                f.write(imgFile[0]['body'])
        except Exception as err:
            log.exception.info(err)
            self.write(self.rsp)
            self.finish()
            return

        self.write({'code': 200, 'msg': 'success'})
        self.finish()

    def is_exist_file_path(self):
        base_dir = os.path.join(self.application.base_dir,
                                'static/uploads/tmp/mch/inlet_excel')
        file_dir = os.path.join(base_dir, '{}'.format(self.current_user))
        file_name = '{}.xls'.format(self.uuid)
        file_path = os.path.join(file_dir, file_name)
        return file_path

    @gen.coroutine
    def create_tmp_image_path(self, imgFile):
        base_dir = os.path.join(self.application.base_dir,
                                'static/uploads/tmp/mch/idcard/')
        file_dir = os.path.join(base_dir, '{}'.format(
            self.current_user), '{}'.format(self.uuid))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_name = imgFile[0]['filename']
        file_path = os.path.join(file_dir, file_name)
        raise gen.Return(file_path)
