# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery.schedules import timedelta, crontab
from kombu import Queue, Exchange
from multiprocessing import cpu_count
from celery import platforms
platforms.C_FORCE_ROOT = True
import sys
sys.path.append('..')
from uline_api.settings import pg_user, pg_passwd, pg_host, pg_db, pg_port, \
    pg_trade_user, pg_trade_passwd, pg_trade_host, pg_trade_db, pg_trade_port

# 定义任务队列
# 路由键以'email'开头的都进email_tasks队列
# 路由键以'inlet'开头的都进inlet_tasks队列
CELERY_QUEUE = (
    Queue('default', Exchange('tasks'), routing_key='task.#'),
    Queue('operation', Exchange('tasks'), routing_key='operation.#'),
    Queue('process', Exchange('tasks'), routing_key='process.#'),
)
CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'task.default'

# 某个程序中出现的队列，在broker中不存在，则立刻创建它
CELERY_CREATE_MISSING_QUEUES = True

# 使用rabbit-mq 作为任务队列
# https://github.com/mher/tornado-celery/blob/master/tcelery/__init__.py#L46
# 似乎只能使用rabbit-mq作为broker
# 使用redis做broker会报错，raise TypeError(repr(o) + " is not JSON serializable")
# BROKER_URL = "redis://localhost:6379/2"
BROKER_URL = "amqp://guest@localhost:5672/"
# CELERY_RESULT_BACKEND = "amqp://"
# 使用amqp做backend会报错，assert self._connection is not None，取不到broker
CELERY_RESULT_BACKEND = "redis://localhost:6379/3"

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'pickle']

# 并发worker数
CELERYD_CONCURRENCY = cpu_count() / 2

CELERY_TIMEZONE = 'Asia/Shanghai'

# 非常重要,有些情况下可以防止死锁
CELERYD_FORCE_EXECV = True

CELERYD_PREFETCH_MULTIPLIER = 1

# 每个worker最多执行完100个任务就会被销毁，可防止内存泄露
CELERYD_MAX_TASKS_PER_CHILD = 100

# CELERYD_TASK_TIME_LIMIT = 60    # 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死
# BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 90}

# 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
CELERY_DISABLE_RATE_LIMITS = True

CELERY_RESULT_DBURI = "postgresql://{}:{}@{}/{}".format(
    pg_user, pg_passwd, pg_host, pg_db)

CELERY_IMPORTS = (
    'uline.backend.risk.query_mch_risk_info',
)
