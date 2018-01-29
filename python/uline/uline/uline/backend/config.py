# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery.schedules import timedelta, crontab
from kombu import Queue, Exchange
from multiprocessing import cpu_count
from celery import platforms
platforms.C_FORCE_ROOT = True
import sys
sys.path.append('..')
from uline.settings import pg_user, pg_passwd, pg_host, pg_db, pg_port, \
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

# 定时任务
CELERYBEAT_SCHEDULE = {
    'generate_mch_inlet_reference': {
        'task': 'uline.backend.dist.generate_mch_inlet_reference.generate_xls',
        'schedule': crontab(minute=30, hour=2),
        'args': ()
    },
    'delete_overdue_report': {
        'task': 'uline.backend.bank.delete_overdue_report.delete_overdue_report',
        'schedule': crontab(minute=30, hour=5),
        'args': ()
    },
    'generate_gather_mchs_activated_email': {
        'task': 'uline.backend.dist.generate_gather_mchs_activated_email.generate_gather_mchs_activated_email',
        'schedule': crontab(minute=10, hour=3),
        'args': ()
    },
    # 'query_and_deal_wx_deal_result': {
    #     'task': 'uline.backend.bank.query_wx_deal_result.query_wx_dine_result',
    #     'schedule': crontab(),
    #     'args': ()
    # }
}

CELERY_RESULT_DBURI = "postgresql://{}:{}@{}/{}".format(
    pg_user, pg_passwd, pg_host, pg_db)

CELERY_RESULT_DB = pg_db
CELERY_RESULT_USER = pg_user
CELERY_RESULT_HOST = pg_host
CELERY_RESULT_PASSWD = pg_passwd
CELERY_RESULT_PORT = pg_port

CELERY_RESULT_TDB = pg_trade_db
CELERY_RESULT_TUSER = pg_trade_user
CELERY_RESULT_THOST = pg_trade_host
CELERY_RESULT_TPASSWD = pg_trade_passwd
CELERY_RESULT_TPORT = pg_trade_port

CELERY_IMPORTS = (
    'uline.backend.tasks',
    # 定时任务
    'uline.backend.dist.generate_mch_inlet_reference',
    'uline.backend.bank.delete_overdue_report',

    # dist任务队列
    'uline.backend.dist.generate_mch_inlet_info',
    'uline.backend.dist.generate_chain_inlet_info',
    'uline.backend.dist.generate_cs_inlet_info',
    'uline.backend.dist.generate_mch_trade_info',
    'uline.backend.dist.generate_mch_refund_info',
    'uline.backend.dist.generate_dist_balance_info',
    'uline.backend.dist.generate_mch_balance_info',
    'uline.backend.dist.generate_transaction_stat_info',
    'uline.backend.dist.generate_mch_statistics',
    'uline.backend.dist.generate_chain_statistics',
    'uline.backend.dist.generate_mch_transaction_stat_info',
    'uline.backend.dist.generate_chain_transaction_stat_info',
    'uline.backend.dist.generate_gather_mchs_activated_email',

    # bank任务队列
    'uline.backend.bank.generate_mch_inlet_info',
    'uline.backend.bank.generate_cs_inlet_info',
    'uline.backend.bank.generate_dist_inlet_info',
    'uline.backend.bank.generate_chain_inlet_info',
    'uline.backend.bank.generate_mch_trade_info',
    'uline.backend.bank.generate_mch_refund_info',
    'uline.backend.bank.generate_dist_balance_info',
    'uline.backend.bank.generate_mch_balance_info',
    'uline.backend.bank.generate_transaction_stat_info',
    'uline.backend.bank.generate_dist_transaction_stat_info',
    'uline.backend.bank.generate_mch_transaction_stat_info',
    'uline.backend.bank.generate_chain_transaction_stat_info',
    'uline.backend.bank.generate_refund_error_info',
    'uline.backend.bank.generate_transaction_error_info',
    'uline.backend.bank.generate_dist_statistics',
    'uline.backend.bank.generate_mch_statistics',
    'uline.backend.bank.generate_chain_statistics',

    'uline.backend.bank.query_wx_deal_result',

    # official任务队列
    'uline.backend.official.generate_mch_inlet_info',
    'uline.backend.official.generate_cs_inlet_info',
    'uline.backend.official.generate_dist_inlet_info',
    'uline.backend.official.generate_chain_inlet_info',
    'uline.backend.official.generate_mch_trade_info',
    'uline.backend.official.generate_mch_refund_info',
    'uline.backend.official.generate_dist_balance_info',
    'uline.backend.official.generate_mch_balance_info',
    'uline.backend.official.generate_transaction_stat_info',
    'uline.backend.official.generate_dist_transaction_stat_info',
    'uline.backend.official.generate_mch_transaction_stat_info',
    'uline.backend.official.generate_chain_transaction_stat_info',
    'uline.backend.official.generate_refund_error_info',
    'uline.backend.official.generate_transaction_error_info',
    'uline.backend.official.generate_dist_statistics',
    'uline.backend.official.generate_mch_statistics',
    'uline.backend.official.generate_chain_statistics',
    'uline.backend.official.generage_message_send_info',

    # merchant任务队列
    'uline.backend.merchant.generate_mch_balance_info',
    'uline.backend.merchant.generate_mch_trade_info',
    'uline.backend.merchant.generate_mch_trade_info_old',
    'uline.backend.merchant.generate_mch_refund_info',
    'uline.backend.merchant.generate_transaction_stat_info',

    # chain任务队列
    'uline.backend.chain.generate_mch_inlet_info',
    'uline.backend.chain.generate_mch_trade_info',
    'uline.backend.chain.generate_mch_refund_info',
    'uline.backend.chain.generate_dist_balance_info',
    'uline.backend.chain.generate_mch_balance_info',
    'uline.backend.chain.generate_transaction_stat_info',
    'uline.backend.chain.generate_mch_statistics',
    'uline.backend.chain.generate_mch_transaction_stat_info',

    # common任务队列
    'uline.backend.common.generate_merchant_bills',
    # 生成商户转入转出信息
    'uline.backend.common.generate_capital_info',

    # inter_bank任务队列
    'uline.backend.inter_bank.generate_dist_inlet_info',
    'uline.backend.inter_bank.generate_mch_inlet_info',
    'uline.backend.inter_bank.generate_cs_inlet_info',
    'uline.backend.inter_bank.generate_chain_inlet_info',
    'uline.backend.inter_bank.generate_mch_balance_info',
    'uline.backend.inter_bank.generate_dist_balance_info',
    'uline.backend.inter_bank.generate_dist_statistics',
    'uline.backend.inter_bank.generate_mch_statistics',
    'uline.backend.inter_bank.generate_transaction_stat_info',
    'uline.backend.inter_bank.generate_dist_transaction_stat_info',
    'uline.backend.inter_bank.generate_mch_transaction_stat_info',
    'uline.backend.inter_bank.generate_mch_trade_info',
    'uline.backend.inter_bank.generate_mch_refund_info',

    # 风险信息
    'uline.backend.risk.query_mch_risk_info',
    'uline.backend.risk.send_trade_risk_info',
)
