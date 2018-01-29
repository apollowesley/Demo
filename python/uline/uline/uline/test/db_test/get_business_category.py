# -*- coding: utf-8 -*-
from uline.public.baseDB import DbClient

db = DbClient()
query = """select industry_code, industry_name from industry_uline_info order by id"""
ret = db.selectSQL(query, fetchone=False)
data = [[r[0], r[1].decode('UTF-8')] for r in ret]
import json
print json.dumps(data, ensure_ascii=False)
# print data
