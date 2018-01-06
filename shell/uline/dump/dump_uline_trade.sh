#!/bin/bash
export PGPASSWORD=#####
db_name=spd_uline_trade
db_user=nbuline

dir_name="./dumpdata/${db_name}_`date +%Y%m%d`"
pg_dump -h 192.168.20.90 -d $db_name  -U $db_user -j 8 -Fd -f $dir_name


