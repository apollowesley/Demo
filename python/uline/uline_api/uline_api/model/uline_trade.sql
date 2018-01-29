--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.14
-- Dumped by pg_dump version 9.5.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: ar_internal_metadata; Type: TABLE; Schema: public; Owner: uline
--

CREATE TABLE ar_internal_metadata (
    key character varying NOT NULL,
    value character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE ar_internal_metadata OWNER TO uline;

--
-- Name: order_refunds; Type: TABLE; Schema: public; Owner: uline
--

CREATE TABLE order_refunds (
    id bigint NOT NULL,
    channel character varying,
    appid character varying,
    mch_id character varying,
    sub_appid character varying,
    sub_mch_id character varying,
    device_info character varying,
    transaction_id character varying,
    out_trade_no character varying,
    out_refund_no character varying,
    total_fee integer,
    total_refund_fee integer,
    refund_fee integer,
    refund_fee_type character varying,
    op_user_id character varying,
    refund_account character varying,
    refund_id character varying,
    refund_channel character varying,
    coupon_refund_fee integer,
    refund_status character varying,
    checked_flag integer,
    ul_mch_id character varying,
    created_at timestamp without time zone,
    mch_trade_no character varying,
    mch_refund_no character varying,
    service_fee integer,
    service_rate double precision
);


ALTER TABLE order_refunds OWNER TO uline;

--
-- Name: order_refunds_id_seq; Type: SEQUENCE; Schema: public; Owner: uline
--

CREATE SEQUENCE order_refunds_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE order_refunds_id_seq OWNER TO uline;

--
-- Name: order_refunds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uline
--

ALTER SEQUENCE order_refunds_id_seq OWNED BY order_refunds.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: uline
--

CREATE TABLE orders (
    id bigint NOT NULL,
    channel character varying,
    appid character varying,
    sub_appid character varying,
    mch_id character varying,
    sub_mch_id character varying,
    device_info character varying,
    body character varying,
    detail character varying,
    attach character varying,
    out_trade_no character varying,
    total_fee integer,
    fee_type character varying,
    spbill_create_ip character varying,
    goods_tag character varying,
    limit_pay character varying,
    auth_code character varying,
    bank_type character varying,
    cash_fee_type character varying,
    cash_fee integer,
    settlement_total_fee integer,
    coupon_fee integer,
    wx_transaction_id character varying,
    time_end character varying,
    trade_type character varying,
    created_at timestamp without time zone,
    complete_at timestamp without time zone,
    notify_url character varying,
    notify_queued boolean,
    notify_count integer,
    notify_successed boolean,
    checked_flag integer,
    trade_state character varying,
    ul_mch_id character varying,
    openid character varying,
    sub_openid character varying,
    mch_trade_no character varying,
    service_fee integer,
    service_rate double precision
);


ALTER TABLE orders OWNER TO uline;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: uline
--

CREATE SEQUENCE orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE orders_id_seq OWNER TO uline;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uline
--

ALTER SEQUENCE orders_id_seq OWNED BY orders.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: uline
--

CREATE TABLE schema_migrations (
    filename text NOT NULL
);


ALTER TABLE schema_migrations OWNER TO uline;

--
-- Name: id; Type: DEFAULT; Schema: public; Owner: uline
--

ALTER TABLE ONLY order_refunds ALTER COLUMN id SET DEFAULT nextval('order_refunds_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: uline
--

ALTER TABLE ONLY orders ALTER COLUMN id SET DEFAULT nextval('orders_id_seq'::regclass);


--
-- Name: ar_internal_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: uline
--

ALTER TABLE ONLY ar_internal_metadata
    ADD CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (key);


--
-- Name: order_refunds_pkey; Type: CONSTRAINT; Schema: public; Owner: uline
--

ALTER TABLE ONLY order_refunds
    ADD CONSTRAINT order_refunds_pkey PRIMARY KEY (id);


--
-- Name: orders_pkey; Type: CONSTRAINT; Schema: public; Owner: uline
--

ALTER TABLE ONLY orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: uline
--

ALTER TABLE ONLY schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (filename);


--
-- PostgreSQL database dump complete
--

