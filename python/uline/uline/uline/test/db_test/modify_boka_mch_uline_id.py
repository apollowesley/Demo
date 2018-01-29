# -*- coding: utf-8 -*-
from os import path
from uline.public.baseDB import DbClient
from xlrd import open_workbook

cur_dir = path.dirname(path.abspath(__file__))
db = DbClient()

category = path.join(cur_dir, 'boka.xls')
wb = open_workbook(category)

bc = wb.sheet_by_index(0)


selQuery = """select industry_code,wx_ind_code, ali_ind_code from industry_uline_info where industry_code=%s;"""
upQuery = """update mch_inlet_info set u_ind_code=%s,wx_ind_code=%s,ali_ind_code=%s where mch_id=%s;"""

db.executeSQL("""update mch_inlet_info set u_ind_code=%s,wx_ind_code=%s,ali_ind_code=%s where mch_id=100000505991;""",
              ('161215010100265', '275', '2015112300111726'))
db.executeSQL("""update mch_inlet_info set u_ind_code=%s,wx_ind_code=%s,ali_ind_code=%s where mch_id=100000503860;""",
              ('161215010100266', '275', '2015112300113179'))


nrows = bc.nrows
try:
    for row in xrange(1, nrows):
        _d = bc.row_values(row)

        ret = db.selectSQL(selQuery, (_d[1], ))
        db.executeSQL(upQuery, (ret[0], ret[1], ret[2], int(_d[0])))
    print 'ok'
except Exception as err:
    print err
