#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '16/1/13'
# sqlacodegen 'postgresql+psycopg2://uline:uline2015@10.17.1.56/uline' > uline_db_schema.py
# sqlacodegen 'postgresql+psycopg2://uline:uline2015@10.17.1.56/uline_trade' > uline_trade_db_schema.py
# 先从本地导出schema
# pg_dump -h 10.17.1.56 -U uline -W -s uline > uline.sql
# pg_dump -h 10.17.1.56 -U uline -W -s uline_trade > uline_trade.sql
