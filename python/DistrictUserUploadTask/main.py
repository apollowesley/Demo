#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import logging.config
import ConfigParser
import string
import os
import sys
import re
import getpass

from task import UploadTask

# 日志
logging.config.fileConfig("./log.conf")
logger = logging.getLogger("example01")

# 获取配置信息


def load_config():

    mysql = {}

    try:
        cf = ConfigParser.ConfigParser()
        cf.read("config.conf")

        # 获取所有节
        secs = cf.sections()
        for sec in secs:
            task = {}
            if sec == "mysql":
                for item in cf.items(sec):
                    mysql[item[0]] = item[1]

    except Exception as e:
        logger.error("加载配置文件出现异常:{}".format(e))

    return mysql


def prn_obj(obj):
    print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])


def main():

    reload(sys)
    sys.setdefaultencoding('utf-8')

    logger.info("准备运行工具")

    # 加载配置文件
    mysql = load_config()

    logger.info("MySQL配置信息为 %s" % str(mysql))

    # 获取目录upload下文件，查看文件命名是否符合要求,如果有不符合退出
    upload_files = os.listdir('./upload')
    if len(upload_files) == 0:
        print("上传目录文件为空，请先放置上传文件")
        return

    for filename in upload_files:
        print(filename)
        if not re.match(".*area_(\d+)_.*\..*", filename):
            print("文件名不符合规范. %s" % filename)
            os.exit(1)

    # 提示输入数据库密码
    password = getpass.getpass("请输入MySQL用户%s密码:" % mysql["username"])
    mysql["password"] = password

    # 遍历查看Excel记录是否符合要求
    logger.info("核对Excel记录是否正确")
    for filename in upload_files:
        task = UploadTask(filename, mysql, logger)
        if not task.verify_records():
            print("上传文件中内容格式有误，请按提示修改后，再执行操作")
            os.exit(1)

    # 执行上传功能
    logger.info("准备写入Excel记录到MySQL上")
    for filename in upload_files:
        task = UploadTask(filename, mysql, logger)
        task.upload()

    logger.info("上传完毕")


if __name__ == "__main__":
    main()