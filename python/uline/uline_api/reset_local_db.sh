#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '2/21/17'

export PGPASSWORD=uline2015

ssh cmbc_dev "PGPASSWORD='uline2015' /usr/bin/pg_dump -h 127.0.0.1 -d uline -U uline -a > /tmp/uline.data"
ssh cmbc_dev "PGPASSWORD='uline2015' /usr/bin/pg_dump -h 127.0.0.1 -d uline -U uline -s > /tmp/uline.schema"
ssh cmbc_dev "PGPASSWORD='uline2015' /usr/bin/pg_dump -h 127.0.0.1 -d uline_trade -U uline -a > /tmp/uline_trade.data"
ssh cmbc_dev "PGPASSWORD='uline2015' /usr/bin/pg_dump -h 127.0.0.1 -d uline_trade -U uline -a > /tmp/uline_trade.schema"

echo '正式环境导出完成,开始下载'
rsync -av --progress -z --compress-level 9 cmbc_dev:/tmp/uline.data cmbc_dev:/tmp/uline.schema cmbc_dev:/tmp/uline_trade.data  cmbc_dev:/tmp/uline_trade.schema .

echo '开始导入到本地'
dropdb -U uline -h 127.0.0.1 uline_trade
dropdb -U uline -h 127.0.0.1 uline

createdb -O uline -U uline uline
createdb -O uline -U uline uline_trade

psql -U uline -h 127.0.0.1 -d uline < uline.schema
psql -U uline -h 127.0.0.1 -d uline < uline.data
psql -U uline -h 127.0.0.1 -d uline_trade < uline_trade.schema
psql -U uline -h 127.0.0.1 -d uline_trade < uline_trade.data