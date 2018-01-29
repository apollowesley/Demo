#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ficapy
# Create: '3/21/17'

import os
from collections import deque
from subprocess import Popen
from wsgiref.simple_server import make_server
import xmlrpc.client
import json
import traceback

PORT = 17864
IP = ['121.201.7.136']
TOKEN = '4f98ae0544c493a299a8ab92636b7c65'
BRANCH = 'stage'
PROJECT_PATH = '/home/deploy/uline'

# 因为gitlab超时时间只有十秒,十秒钟是部署不完的,会导致多次重试
validate = deque(maxlen=10)


def update_code():
    # git config credential.helper 'cache --timeout=36000'
    os.chdir(PROJECT_PATH)
    Popen('git clean -df', shell=True).wait()
    Popen('git reset --hard', shell=True).wait()
    Popen(['git', 'pull', 'origin', BRANCH]).wait()


def restart_process():
    try:
        s = xmlrpc.client.ServerProxy('http://localhost:9001')
        s.supervisor.stopProcess("celery")
        s.supervisor.startProcess("celery")
        for i in range(1, 9):
            s.supervisor.stopProcess("uline_cms:pyuline%s" % i)
            s.supervisor.startProcess("uline_cms:pyuline%s" % i)
        # s.supervisor.stopProcessGroup("uline_cms")
        # s.supervisor.startProcessGroup("uline_cms")
    except Exception as e:
        traceback.print_exc(e)


def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    remote = environ.get('HTTP_X_REAL_IP') or environ.get('REMOTE_ADDR')
    success, fail = [b"Success"], [b'Fail']
    if IP and remote not in IP:
        print('invalid ip')
        return fail
    if TOKEN and TOKEN not in environ.get('QUERY_STRING'):
        print('invalid token')
        return fail

    length = int(environ.get('CONTENT_LENGTH', '0'))

    body = environ['wsgi.input'].read(length)
    body = json.loads(body.decode())
    checkout_sha = body.get('checkout_sha')
    if checkout_sha in validate:
        print('invalid requests')
        return fail
    validate.append(checkout_sha)
    if body.get('object_kind') == "push" and body.get('ref').lower() == "refs/heads/" + BRANCH.lower():
        update_code()
        restart_process()
    print(success)
    return success


make_server('', PORT, simple_app).serve_forever()
