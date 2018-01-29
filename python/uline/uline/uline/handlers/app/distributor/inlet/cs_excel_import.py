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
import os
import uuid
from tornado.web import authenticated, asynchronous
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from xlrd import open_workbook
from uline.handlers.baseHandlers import DtAdminHandler
from uline.public import log
from .form import UploadCSInletExcel
from uline.public.constants import CS_EXCEL_TEMPLATE_PATH
from uline.public.permit import check_permission


class ImportCSExcelHandler(DtAdminHandler):
    executor = ThreadPoolExecutor(16)

    @authenticated
    @check_permission
    def prepare(self):
        self.form = UploadCSInletExcel(self)
        self.form.xls_file.raw_data = self.request.files['xls_file']

    def check_xsrf_cookie(self):
        pass

    @run_on_executor
    @asynchronous
    @gen.coroutine
    def post(self):
        if not self.form.validate():
            self.write({'code': 406, 'msg': 'fail'})

        excelFile = self.request.files.get('xls_file')
        excel_path = yield self.create_file_path()
        file_path, file_name = excel_path[0], excel_path[1]
        uuid = file_name.split('.')[0]
        try:
            yield self.save_mch_inlet_excel(file_path, excelFile)
            check_flag = yield self.check_excel(file_path)
            if not check_flag:
                msg = """您的进件模板是旧版，请下载新版的模板，填写后重新上传。如使用新模板仍能看到此提示，请联系管理员。"""
                self.write({'code': 407, 'msg': msg, 'uuid': uuid})
                self.finish()
                return
        except Exception as err:
            log.exception.info(err)
            self.write({'code': 406, 'msg': 'fail'})
            self.finish()
            return

        self.write({'code': 200, 'msg': 'success', 'uuid': uuid})
        self.finish()
        return

    @gen.coroutine
    def create_file_path(self):
        base_dir = os.path.join(
            self.application.base_dir, 'static/uploads/tmp/mch/inlet_excel')
        file_dir = os.path.join(base_dir, '{}'.format(self.current_user))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_name = '{}.xls'.format(uuid.uuid4().hex)
        file_path = os.path.join(file_dir, file_name)
        raise gen.Return([file_path, file_name])

    @gen.coroutine
    def save_mch_inlet_excel(self, file_path, excelFile):
        data = excelFile[0]['body']
        with open(file_path, 'wb') as f:
            f.write(data)
            f.close()

    @gen.coroutine
    def check_excel(self, file_path):
        wb = open_workbook(file_path)
        check_flag = False
        try:
            mch_info = wb.sheet_by_index(0)
            # 获取系统进件模板
            wb_template = open_workbook(self.get_excel_template_path())
            info_template = wb_template.sheet_by_index(0)
            # 判断标题是否相同
            if str(mch_info.row(0)) == str(info_template.row(0)):
                check_flag = True
        except Exception as err:
            log.exception.info(err)
        raise gen.Return(check_flag)

    def get_excel_template_path(self):
        file_path = os.path.join(self.application.base_dir,
                                 CS_EXCEL_TEMPLATE_PATH)
        if os.path.exists(file_path):
            return file_path
        else:
            return False
