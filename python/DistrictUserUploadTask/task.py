# -*- coding:utf-8 -*-
# 上传包括小区用户数据Excel文档到指定的MySQL表
# 初始化，传来文件路径
# VerifyRecords 检查所有记录
# Upload
#

import re
import xlrd
import MySQLdb
import time
import shutil
import xlwt


class UploadTask:
    def __init__(self, excel_path, mysql, logger):

        self.excel_path = excel_path
        self.mysql = mysql
        self.logger = logger

    def get_area_id(self):
        areaid = re.match(".*area_(\d+)_.*\..*", self.excel_path).group(1)
        return areaid

    def verify_records(self):

        errors = []

        # 遍历Excel文件记录，查看每条记录是否符合指定的要求
        # 如果不符合

        book = xlrd.open_workbook("./upload/%s" % self.excel_path)
        sheet = book.sheet_by_index(0)
        rows = sheet.nrows
        cols = sheet.ncols

        # 遍历行数
        for r in range(1, sheet.nrows):
            address = sheet.cell(r, 0).value
            contactnames = sheet.cell(r, 1).value
            contactphones = sheet.cell(r, 2).value

            # 查看电话号码是否正确
            # regex = "^((13[0-9])|(14[5|7])|(15([0-3]|[5-9]))|(18[0,5-9]))\d{8}$"
            # errors.append(show.row_values)

        if len(errors) == 0:
            return True
        else:
            self.logger.error("出现错误 %s" % str(errors))
            return False

    def save_error_rows(self, error_rows):

        book = xlwt.Workbook()  # 创建工作簿
        sheet = book.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 创建sheet

        row_num = 0
        for row in error_rows:
            for i in range(0, len(row)):
                sheet.write(row_num, i, row[i])
            row_num += 1
        book.save("./error/%s" %
                  self.excel_path.replace(".xlsx", ".xls"))  # 保存文件
        self.logger.info("错误行处理完毕")

    def upload(self):

        # 上传记录
        # 遍历Excel文件记录，查看每条记录是否符合指定的要求
        book = xlrd.open_workbook("./upload/%s" % self.excel_path)
        sheet = book.sheet_by_index(0)
        rows = sheet.nrows
        cols = sheet.ncols

        self.logger.info("行数：%d, 列数:%d" % (rows, cols))

        area_id = self.get_area_id()
        self.logger.info("地区ID为:%s" % area_id)

        # 连接数据库
        conn = MySQLdb.connect(charset="utf8", host=self.mysql["host"], port=int(self.mysql["port"]),
                               user=self.mysql["username"], passwd=self.mysql["password"], db=self.mysql["dbname"])
        cursor = conn.cursor()

        # 创建插入SQL语句
        sql_insert = """INSERT INTO t_district_users (garden_id, address, contact_name, contact_phones, note,create_at)
                VALUES (%s, %s, %s, %s, %s,%s)"""
        sql_update = """UPDATE t_district_users SET address = %s , contact_name = %s, note = %s
                 where garden_id = %s and contact_phones = %s """

        errors = []  # 错误行数
        # 遍历行数

        flag = 0
        for r in range(1, sheet.nrows):

            flag += 1

            address = sheet.cell(r, 0).value
            name = sheet.cell(r, 1).value
            phones = sheet.cell(r, 2).value

            note = ""

            if isinstance(phones, (float, int)):
                phones = str(int(phones))

            # 备注
            if cols > 4:
                note = "%s %s" % (sheet.cell(r, 3).value,
                                  sheet.cell(r, 4).value)
            elif cols == 4:
                note = "%s" % sheet.cell(r, 3).value

            if address.strip() == "" or name.strip() == "" or phones.strip() == "":
                # 写记录
                row = [address, name, phones, note]
                errors.append(row)
                # 继续下一个
                continue

            curr_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            values = (area_id, address, name, phones, note, curr_time)

            # 是否已有记录 areaid + phones
            sql0 = "select * from t_district_users where garden_id = %s and address = '%s'" % (
                area_id, address)
            self.logger.debug(sql0)
            match_counts = cursor.execute(sql0)
            if match_counts > 0:
                # 已存在记录
                values = (address, name, phones, area_id, note)
                self.logger.info("更新第%d条数据：%s:%s" % (flag, name, phones))
                sql = sql_update % values
                self.logger.debug(sql)
                cursor.execute(sql_update, values)
            else:
                self.logger.info("添加第%d条数据：%s:%s" % (flag, name, phones))
                sql = sql_insert % values
                self.logger.debug(sql)
                cursor.execute(sql_insert, values)
            # 提交
            conn.commit()

        # 关闭游标
        cursor.close()

        # u关闭
        conn.close()

        src_path = "./upload/%s" % self.excel_path
        dest_path = "./done/%s" % self.excel_path
        shutil.move(src_path, dest_path)

        # 是否有错误行
        if len(errors) > 0:
            self.logger.info("处理错误行，错误行数：%d" % len(errors))
            self.save_error_rows(errors)

        self.logger.info("文件处理完毕")
