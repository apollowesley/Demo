### 接入支付宝（数据库修改）

#### 1. 创建行业类别数据表
```
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
```

#### 2. 添加和更正进件信息表的字段
```
alter table mch_inlet_info add COLUMN u_ind_code VARCHAR(40);
alter table mch_inlet_info add COLUMN wx_ind_code VARCHAR(40);
alter table mch_inlet_info add COLUMN ali_ind_code VARCHAR(40);
alter table mch_inlet_info add COLUMN old_ind_code VARCHAR(40);

alter table dt_inlet_info add COLUMN u_ind_code VARCHAR(40);
alter table dt_inlet_info add COLUMN wx_ind_code VARCHAR(40);
alter table dt_inlet_info add COLUMN ali_ind_code VARCHAR(40);
alter table dt_inlet_info add COLUMN old_ind_code VARCHAR(40);
```

#### 3. 更新进件信息表
```
update mch_inlet_info set old_ind_code=(select industry_code from industry_info where id=mch_inlet_info.industry_type);
update dt_inlet_info set old_ind_code=(select industry_code from industry_info where id=dt_inlet_info.industry_type);

alter table mch_inlet_info drop column industry_type;
alter table dt_inlet_info drop column industry_type;
```