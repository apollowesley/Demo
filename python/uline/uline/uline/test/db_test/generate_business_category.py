# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from xlrd import open_workbook
from uline.public.baseDB import DbClient
from os import path

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

cur_dir = path.dirname(path.abspath(__file__))

db_schema = """
create table industry_uline_info (
  id SERIAL PRIMARY KEY ,
  industry_code VARCHAR(40) not null,
  industry_name VARCHAR(200) not null,
  wx_ind_code VARCHAR(40),
  ali_ind_code VARCHAR(40),
  status int not null default 1,
  create_at timestamp not null default CURRENT_TIMESTAMP,
  update_at timestamp not null default CURRENT_TIMESTAMP
);
create  UNIQUE INDEX industry_uline_info_index
  ON industry_uline_info
  USING btree
  (industry_code);


create table industry_wx_info (
  id SERIAL PRIMARY KEY ,
  industry_code VARCHAR(40) not null,
  industry_name VARCHAR(200) not null,
  status int not null DEFAULT 1,
  create_at timestamp not null default CURRENT_TIMESTAMP,
  update_at timestamp not null default CURRENT_TIMESTAMP
);
create  UNIQUE INDEX industry_wx_info_index
  ON industry_wx_info
  USING btree
  (industry_code);

create table industry_ali_info (
  id SERIAL PRIMARY KEY ,
  industry_code VARCHAR(40) not null,
  industry_name VARCHAR(200) not null,
  status int not null DEFAULT 1,
  create_at timestamp not null default CURRENT_TIMESTAMP,
  update_at timestamp not null default CURRENT_TIMESTAMP
);
create  UNIQUE INDEX industry_ali_info_index
  ON industry_ali_info
  USING btree
  (industry_code);

"""


db = DbClient()
db.executeSQL("""drop table if EXISTS industry_uline_info;drop table if EXISTS industry_wx_info;drop table if EXISTS industry_ali_info;""")
db.executeSQL(db_schema)

category = path.join(cur_dir, 'business_category.xlsx')
wb = open_workbook(category)

bc = wb.sheet_by_index(0)

nrows = bc.nrows
ali_data_d, wx_data_d = dict(), dict()
uline_data = list()

for row in xrange(1, nrows):
    _d = bc.row_values(row)
    u_name = str(_d[2]) + '-' + str(_d[3]) + '-' + str(_d[4]) + '-' + str(_d[5])
    u_info = (u_name, _d[6], _d[9], _d[13], _d[1])
    uline_data.append(u_info)

    # if _d[2] in ['1', 1]:
    #     wx_name = str(_d[2]) + '-' + str(_d[7]) + '-' + str(_d[8])
    #     wx_info = (wx_name, _d[9])
    #     wx_data_d.update({_d[9]: wx_info})

    ali_name = str(_d[10]) + '-' + str(_d[11]) + '-' + str(_d[12])
    ali_info = (ali_name, _d[13])
    ali_data_d.update({_d[13]: ali_info})

ali_data = ali_data_d.values()
# wx_data = wx_data_d.values()

query = """insert into industry_uline_info (industry_name, industry_code, wx_ind_code, ali_ind_code, status) values (%s, %s, %s, %s, %s)"""
db.executeSQL(query, uline_data)

# query = """insert into industry_wx_info (industry_name, industry_code) values (%s, %s)"""
# db.executeSQL(query, wx_data)
query = """insert into industry_wx_info (industry_name, industry_code) select industry_name, industry_code from industry_info"""
db.executeSQL(query)

query = """insert into industry_ali_info (industry_name, industry_code) values (%s, %s)"""
db.executeSQL(query, ali_data)

alter_schema = """
alter table mch_inlet_info add COLUMN u_ind_code VARCHAR(40);
alter table mch_inlet_info add COLUMN wx_ind_code VARCHAR(40);
alter table mch_inlet_info add COLUMN ali_ind_code VARCHAR(40);
alter table mch_inlet_info add COLUMN old_ind_code VARCHAR(40);

alter table dt_inlet_info add COLUMN u_ind_code VARCHAR(40);
alter table dt_inlet_info add COLUMN wx_ind_code VARCHAR(40);
alter table dt_inlet_info add COLUMN ali_ind_code VARCHAR(40);
alter table dt_inlet_info add COLUMN old_ind_code VARCHAR(40);

alter table mch_user add COLUMN ali_sub_mch_id VARCHAR(64);
"""
db.executeSQL(alter_schema)

update_schema = """
update mch_inlet_info set old_ind_code=(select industry_code from industry_info where id=mch_inlet_info.industry_type);
update dt_inlet_info set old_ind_code=(select industry_code from industry_info where id=dt_inlet_info.industry_type);

alter table mch_inlet_info drop column industry_type;
alter table dt_inlet_info drop column industry_type;
"""
db.executeSQL(update_schema)
