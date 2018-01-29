create sequence tb_mch_id_seq increment by 1 minvalue 1000000000 no maxvalue start with 1000000000;
create sequence tb_dt_id_seq increment by 1 minvalue 10000000 maxvalue 99999999 start with 10000000;
create sequence tb_bk_id_seq increment by 1 minvalue 10000000 maxvalue 99999999 start with 10000000;
create sequence tb_ub_id_seq increment by 1 minvalue 100000 maxvalue 999999 start with 100000;
CREATE SEQUENCE recon_refund_error_info_id_seq increment by 1 minvalue 10000000 no maxvalue start with 10000000;

-- 商户进件信息表（mch_inlet_info）
CREATE TABLE mch_inlet_info
(
    mch_id BIGINT PRIMARY KEY NOT NULL,
    mch_name VARCHAR(64) NOT NULL,
    mch_shortname VARCHAR(64) NOT NULL,
    dt_id BIGINT NOT NULL,
    industry_type INTEGER NOT NULL,
    province VARCHAR(32) NOT NULL,
    city VARCHAR(32) NOT NULL,
    address VARCHAR(255) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    mobile VARCHAR(11) NOT NULL,
    service_phone VARCHAR(15) NOT NULL,
    email VARCHAR(64) NOT NULL,
    id_card_img_f VARCHAR(200) NOT NULL,
    id_card_img_b VARCHAR(200) NOT NULL,
    auth_status INTEGER DEFAULT 0 NOT NULL,
    activated_status INTEGER DEFAULT 0 NOT NULL,
    auth_at TIMESTAMP DEFAULT now() NOT NULL,
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX mch_inlet_info_mobile_uindex ON mch_inlet_info (mobile);
CREATE UNIQUE INDEX mch_inlet_info_email_uindex ON mch_inlet_info (email);
CREATE INDEX mch_inlet_info_index ON mch_inlet_info (mch_id);

-- 行业信息表(industry_info)
create table industry_info(
    id serial primary key,
    industry_name varchar(200),
    industry_code character varying(40) NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX industry_info_index
  ON industry_info
  USING btree
  (id);

-- 商户结算账户表(mch_balance)
create table mch_balance (
    mch_id bigint not null primary key,
    balance_type int not null default 0,
    balance_name varchar(64) not null,
    bank_no varchar(64) not null,
    balance_account varchar(64) not null,
    id_card_no varchar(20),
    create_at timestamp not null default CURRENT_TIMESTAMP,
    update_at timestamp not null default CURRENT_TIMESTAMP
);
create  UNIQUE INDEX mch_balance_index
  ON public.mch_balance
  USING btree
  (mch_id);

-- 商户支付方式表(mch_payment)
create table mch_payment (
    id serial not null primary key,
    mch_id bigint not null,
    payment_type int not null,
    payment_rate int not null,
    activated_status int not null,
    create_at timestamp not null default CURRENT_TIMESTAMP,
    update_at timestamp not null default CURRENT_TIMESTAMP
);
create  UNIQUE INDEX mch_payment_index
  ON public.mch_payment
  USING btree
  (id);

-- 商户用户信息表(mch_user)
CREATE TABLE mch_user
(
    mch_id BIGINT PRIMARY KEY NOT NULL,
    mch_name VARCHAR(64) NOT NULL,
    email VARCHAR(64) NOT NULL,
    password VARCHAR(64) NOT NULL,
    wx_sub_mch_id VARCHAR(64) NOT NULL,
    mch_pay_key VARCHAR(64) NOT NULL,
    status INTEGER NOT NULL,
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX mch_user_index ON mch_user (mch_id);
CREATE UNIQUE INDEX mch_user_email_uindex ON mch_user (email);

-- 渠道商进件信息表(dt_inlet_info)
CREATE TABLE dt_inlet_info
(
    dt_id BIGINT PRIMARY KEY NOT NULL,
    dt_name VARCHAR(64) NOT NULL,
    industry_type INTEGER NOT NULL,
    province VARCHAR(32) NOT NULL,
    city VARCHAR(32) NOT NULL,
    address VARCHAR(255) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    mobile VARCHAR(11) NOT NULL,
    email VARCHAR(64) NOT NULL,
    id_card_img_f VARCHAR(200) NOT NULL,
    id_card_img_b VARCHAR(200) NOT NULL,
    auth_status INTEGER NOT NULL,
    activated_status INTEGER NOT NULL,
    auth_at TIMESTAMP,
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX dt_inlet_info_mobile_uindex ON dt_inlet_info (mobile);
CREATE UNIQUE INDEX dt_inlet_info_email_uindex ON dt_inlet_info (email);
CREATE INDEX dt_inlet_info_index ON dt_inlet_info (dt_id);

-- 渠道商结算账户表(dt_balance)
CREATE TABLE dt_balance
(
    dt_id BIGINT PRIMARY KEY NOT NULL,
    balance_type INTEGER NOT NULL,
    balance_name VARCHAR(64) NOT NULL,
    bank_no VARCHAR(64) NOT NULL,
    balance_account VARCHAR(64),
    id_card_no VARCHAR(20),
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX dt_balance_index ON dt_balance (dt_id);

-- 渠道商支付方式表(dt_payment)
create table dt_payment (
    id serial not null primary key,
    dt_id bigint not null,
    payment_type int not null,
    payment_rate int not null,
    activated_status int not null,
    create_at timestamp not null default CURRENT_TIMESTAMP,
    update_at timestamp not null default CURRENT_TIMESTAMP
);
create  UNIQUE INDEX dt_payment_index
  ON public.dt_payment
  USING btree
  (id);

-- 渠道商用户信息表(dt_user)
CREATE TABLE dt_user
(
    dt_id BIGINT PRIMARY KEY NOT NULL,
    dt_name VARCHAR(64) NOT NULL,
    email VARCHAR(64) NOT NULL,
    password VARCHAR(64) NOT NULL,
    status int default 0 not null,
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX dt_user_index ON dt_user (dt_id);
CREATE UNIQUE INDEX dt_user_email_uindex ON dt_user (email);

-- 银行用户信息表(bk_user)
CREATE TABLE bk_user
(
    bk_id INTEGER PRIMARY KEY NOT NULL,
    bk_name varchar(64) not null,
    email VARCHAR(64) NOT NULL,
    password VARCHAR(64) NOT NULL,
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX bk_user_index ON bk_user (bk_id);
CREATE UNIQUE INDEX bk_user_email_uindex ON bk_user (email);

-- 渠道清分信息表(dt_clear_info)
CREATE TABLE dt_clear_info
(
    dt_clear_no BIGINT PRIMARY KEY NOT NULL,
    dt_id BIGINT NOT NULL,
    mch_id BIGINT NOT NULL,
    dt_daily_balance_no BIGINT,
    out_trade_no VARCHAR(32) NOT NULL,
    trade_amount BIGINT NOT NULL,
    profit_rate INTEGER NOT NULL,
    dt_profit int NOT NULL,
    create_at TIMESTAMP DEFAULT now() NOT NULL,
    update_at TIMESTAMP DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX dt_clear_info_dt_clear_no_uindex ON dt_clear_info (dt_clear_no);

-- 商户清分信息表(mch_clear_info)
CREATE TABLE mch_clear_info
(
    mch_clear_no BIGINT PRIMARY KEY NOT NULL,
    mch_id BIGINT NOT NULL,
    out_trade_no VARCHAR(32) NOT NULL,
    mch_daily_balance_no BIGINT,
    trade_amount BIGINT NOT NULL,
    profit_rate INTEGER NOT NULL,
    mch_profit int NOT NULL,
    create_at TIMESTAMP NOT NULL,
    update_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX mch_clear_info_mch_clear_no_uindex ON mch_clear_info (mch_clear_no);

-- 平台清分信息表(mch_clear_info)
CREATE TABLE p_clear_info
(
    p_clear_no BIGINT PRIMARY KEY NOT NULL,
    out_trade_no VARCHAR(32) NOT NULL,
    p_daily_balance_no BIGINT,
    trade_amount BIGINT NOT NULL,
    profit_rate INTEGER NOT NULL,
    p_profit int NOT NULL,
    create_at TIMESTAMP NOT NULL,
    update_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX p_clear_info_p_clear_no_uindex ON p_clear_info (p_clear_no);

-- 商户结算信息表(mch_daily_balance_info)
CREATE TABLE mch_daily_balance_info
(
    mch_daily_balance_no BIGINT PRIMARY KEY NOT NULL,
    mch_id BIGINT NOT NULL,
    busiType SMALLINT NOT NULL,
    rcvAcctNo VARCHAR(64) NOT NULL,
    rcvBankName  VARCHAR(128) NOT NULL,
    rcvBankSettleNo  VARCHAR(12) NOT NULL,
    rcvAcctName VARCHAR(64) NOT NULL,
    tranAmt BIGINT NOT NULL,
    need_pay_time TIMESTAMP NOT NULL,
    pay_start_time TIMESTAMP,
    pay_end_time TIMESTAMP,
    pay_status SMALLINT NOT NULL,
    failure_details VARCHAR(128),
    check_status SMALLINT NOT NULL,
    day_tx_amount BIGINT NOT NULL,
    day_refund_amount BIGINT NOT NULL,
    day_tx_net_amout BIGINT NOT NULL,
    day_profit_amount BIGINT NOT NULL,
    day_tx_count BIGINT NOT NULL,
    day_refund_count BIGINT NOT NULL,
    create_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX mch_daily_balance_info_mch_daily_balance_no_uindex ON mch_daily_balance_info (mch_daily_balance_no);

-- 渠道商结算信息表(dt_daily_balance_info)
CREATE TABLE dt_daily_balance_info
(
    dt_daily_balance_no BIGINT PRIMARY KEY NOT NULL,
    dt_id BIGINT NOT NULL,
    busiType SMALLINT NOT NULL,
    rcvAcctNo VARCHAR(64) NOT NULL,
    rcvBankName  VARCHAR(128) NOT NULL,
    rcvBankSettleNo  VARCHAR(12) NOT NULL,
    rcvAcctName VARCHAR(64) NOT NULL,
    tranAmt BIGINT NOT NULL,
    need_pay_time TIMESTAMP NOT NULL,
    pay_start_time TIMESTAMP,
    pay_end_time TIMESTAMP,
    pay_status SMALLINT NOT NULL,
    failure_details VARCHAR(128),
    check_status SMALLINT NOT NULL,
    day_tx_amount BIGINT NOT NULL,
    day_refund_amount BIGINT NOT NULL,
    day_tx_net_amout BIGINT NOT NULL,
    day_profit_amount BIGINT NOT NULL,
    day_tx_count BIGINT NOT NULL,
    day_refund_count BIGINT NOT NULL,
    create_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX dt_daily_balance_info_dt_daily_balance_no_uindex ON dt_daily_balance_info (dt_daily_balance_no);

-- 平台结算信息表(p_daily_balance_info)
CREATE TABLE p_daily_balance_info
(
    p_daily_balance_no BIGINT PRIMARY KEY NOT NULL,
    busiType SMALLINT NOT NULL,
    rcvAcctNo VARCHAR(64) NOT NULL,
    rcvBankName  VARCHAR(128) NOT NULL,
    rcvBankSettleNo  VARCHAR(12) NOT NULL,
    rcvAcctName VARCHAR(64) NOT NULL,
    tranAmt BIGINT NOT NULL,
    need_pay_time TIMESTAMP NOT NULL,
    pay_start_time TIMESTAMP,
    pay_end_time TIMESTAMP,
    pay_status SMALLINT NOT NULL,
    failure_details VARCHAR(128),
    check_status SMALLINT NOT NULL,
    day_tx_amount BIGINT NOT NULL,
    day_refund_amount BIGINT NOT NULL,
    day_tx_net_amout BIGINT NOT NULL,
    day_profit_amount BIGINT NOT NULL,
    day_tx_count BIGINT NOT NULL,
    day_refund_count BIGINT NOT NULL,
    create_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX p_daily_balance_info_p_daily_balance_no_uindex ON p_daily_balance_info (p_daily_balance_no);

-- 结算银行信息表(balance_bank_info)
CREATE TABLE balance_bank_info
(
  id serial not null primary key,
  bank_name varchar(64) not null,
    bank_no varchar(64) not null
);
CREATE INDEX balance_bank_info_index
  ON balance_bank_info
  USING btree
  (id);

-- 对账交易异常信息表(recon_tx_error_info)
CREATE TABLE recon_tx_error_info
(
    id SERIAL PRIMARY KEY NOT NULL,
    out_trade_no VARCHAR(32) NOT NULL,
    detail VARCHAR(2048) NOT NULL,
    handle_status SMALLINT NOT NULL,
    except_type SMALLINT NOT NULL,
    description VARCHAR(64),
    create_at TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX recon_tx_error_info_id_uindex ON public.recon_tx_error_info (id);


-- 对账退款异常信息表(recon_refund_error_info)
CREATE TABLE recon_refund_error_info (
  id INTEGER PRIMARY KEY NOT NULL DEFAULT nextval('recon_refund_error_info_id_seq'::regclass),
  out_refund_no CHARACTER VARYING(32) NOT NULL,
  detail CHARACTER VARYING(2048) NOT NULL,
  handle_status SMALLINT NOT NULL,
  except_type SMALLINT NOT NULL,
  description VARCHAR(2048),
  create_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX recon_refund_error_info_id_uindex ON recon_refund_error_info USING BTREE (id);

-- 官方用户表(ub_user)
create table ub_user (
    ub_id int not null default nextval('tb_ub_id_seq'),
    ub_name varchar(16) not null,
    email varchar(64) not null,
    password varchar(64) not null,
    create_at timestamp without time zone NOT NULL DEFAULT now(),
    update_at timestamp without time zone NOT NULL DEFAULT now(),
   CONSTRAINT ub_user_pkey PRIMARY KEY (ub_id)
);
CREATE UNIQUE INDEX ub_user_index ON ub_user USING btree (ub_id);

-- 商户审核详情记录表(auth_mch_info)
create table auth_mch_info (
    id serial not null primary key,
    mch_id bigint not null,
    comment varchar(64) not null,
    auth_status int not null default 0,
    create_at timestamp not null default CURRENT_TIMESTAMP
 );
create UNIQUE INDEX auth_mch_info_index ON public.auth_mch_info USING btree (id);

-- 渠道商审核详情记录表(auth_dt_info)
create table auth_dt_info (
    id serial not null primary key,
    dt_id bigint not null,
    comment varchar(64) not null,
    auth_status int not null default 0,
    create_at timestamp not null default CURRENT_TIMESTAMP
 );
create UNIQUE INDEX auth_dt_info_index ON public.auth_dt_info USING btree (id);

-- 商户支付方式激活详情记录表(activated_mch_info)
create table activated_mch_info (
    id serial not null primary key,
    mch_id bigint not null,
    payment_type int not null default 0,
    comment varchar(64) not null,
    activated_status int not null default 0,
    create_at timestamp not null default CURRENT_TIMESTAMP
 );
create UNIQUE INDEX activated_mch_info_index ON public.activated_mch_info USING btree (id);

-- 渠道商支付方式激活详情记录表(activated_dt_info)
create table activated_dt_info (
    id serial not null primary key,
    dt_id bigint not null,
    payment_type int not null default 0,
    comment varchar(64) not null,
    activated_status int not null default 0,
    create_at timestamp not null default CURRENT_TIMESTAMP
 );
create UNIQUE INDEX activated_dt_info_index ON public.activated_dt_info USING btree (id);

-- 微信对平台上的固定费率(wx_fixed_rate)
CREATE TABLE wx_fixed_rate
(
    id serial NOT NULL,
    rate integer NOT NULL,
    payment_type integer NOT NULL ,
    create_at timestamp without time zone NOT NULL,
    PRIMARY KEY (id)
);

-- 商户进件到微信的记录信息
CREATE TABLE mch_inlet_to_wx_info
(
    id serial NOT NULL,
    mch_id bigint NOT NULL,
    return_msg varchar(64) not null,
    return_code varchar(64) not null,
    result_msg varchar(64) not null,
    result_code varchar(64) not null,
    create_at timestamp without time zone NOT NULL,
    PRIMARY KEY (id)
)