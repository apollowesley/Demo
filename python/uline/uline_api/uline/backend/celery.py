# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery
# 启动celery并设置用-B参数启动beat进行定时任务的调度
# celery worker -l info -A uline --app=uline.backend.celery -B -Ofair
app = Celery('backend')
app.config_from_object('uline.backend.config')

if __name__ == '__main__':
    app.start()
