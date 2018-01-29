# -*- coding: utf-8 -*-
from uline.backend.__init__ import *
from openpyxl import Workbook
from zipfile import ZipFile
from os import path

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
from uline.public import log

# 任务计划
# 生成支行信息表格


@app.task
def generate_xls():
    # xlrw会报错：aised unexpected: ValueError('row index was 65536, not allowed by .xls format',)
    # openpyxl支持更多行数的写入
    wb = Workbook()
    ws = wb.create_sheet(u'支行联行号信息', 0)
    fields = [u'支行名称', u'支行联行号']
    ws.append(fields)
    query = """select bank_name,bank_no from balance_bank_info;"""
    ret = db.selectSQL(query, fetchone=False)

    for data in ret:
        ws.append(list(data))

    bank_info_path = cur_dir + '/static/handbook/ULINE_BANK_INFO.xlsx'
    wb.save(bank_info_path)
    area_info_path = cur_dir + '/static/handbook/ULINE_AREA_INFO.xlsx'
    business_cat_info_path = cur_dir + \
        '/static/handbook/ULINE_BUSINESS_CATEGORY_INFO.xlsx'
    file_path = cur_dir + '/static/handbook/ULINE_INLET_INFO_REFERENCE.zip'
    with ZipFile(file_path, 'w') as zf:
        try:
            zf.write(area_info_path, arcname='ULINE_AREA_INFO.xlsx')
            zf.write(business_cat_info_path,
                     arcname='ULINE_BUSINESS_CATEGORY_INFO.xlsx')
            zf.write(bank_info_path, arcname='ULINE_BANK_INFO.xlsx')
        except Exception as err:
            log.exception.info(err)
        finally:
            zf.close()
