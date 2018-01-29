#!/usr/bin/env bash
export PGPASSWORD=uline2015

dropdb -U uline -h 127.0.0.1 uline_trade
dropdb -U uline -h 127.0.0.1 uline

createdb -O uline  uline
createdb -O uline  uline_trade

psql -U uline -h 127.0.0.1 -d uline < stage/uline.data
psql -U uline -h 127.0.0.1 -d uline_trade < stage/uline_trade.data
