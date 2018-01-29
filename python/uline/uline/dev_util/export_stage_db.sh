ssh cmbc_dev "PGPASSWORD='uline2015' /usr/bin/pg_dump -h 127.0.0.1 -d uline -U uline > /tmp/uline.data"
ssh cmbc_dev "PGPASSWORD='uline2015' /usr/bin/pg_dump -h 127.0.0.1 -d uline_trade -U uline > /tmp/uline_trade.data"

echo '正式环境导出完成,开始下载'
rsync -av --progress -z --compress-level 9 cmbc_dev:/tmp/uline_trade.data stage/
rsync -av --progress -z --compress-level 9 cmbc_dev:/tmp/uline.data stage/
