#!/usr/bin/env bash

#将dev环境的数据同步到本地文件夹方便测试
current="$(pwd)"
parentdir="$(dirname "$current")"
jojndir="/uline/static/uploads"
rsync -avz --partial --compress-level 9 --progress --stats --delete cmbc_dev:~/uline/uline/static/uploads/ $parentdir$jojndir