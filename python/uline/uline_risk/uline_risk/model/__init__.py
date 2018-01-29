#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '16/1/13'
# sqlacodegen 'postgresql+psycopg2://uline:uline2015@127.0.0.1/uline' > uline_db_schema.py
# sqlacodegen 'postgresql+psycopg2://uline:uline2015@127.0.0.1/uline_trade' > uline_trade_db_schema.py
# 先从本地导出schema
# pg_dump -h 10.17.1.56 -U uline -W -s uline > uline_risk.sql
# pg_dump -h 10.17.1.56 -U uline -W -s uline_trade > uline_trade.sql

# pgdiff -U uline -H 10.17.1.56 -D uline -W uline2015 -O "sslmode=disable"
# -u ulinesa -h  -p 20968 -w '' -d uline -o "sslmode=disable" INDEX
# 线上环境
# sqlacodegen 'postgresql+psycopg2://ulinesa:Xm.u7!nebio2@1.tcp.ap.ngrok.io:20968/uline' > uline_db_schema.py
