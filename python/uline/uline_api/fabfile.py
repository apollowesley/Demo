# -*-coding:utf-8 -*-

# fab deploy:dev

import time
import os
import sys
from fabric.api import run, env, cd, sudo

env.use_ssh_config = True
deploy_env = sys.argv[-1].split(':')[-1].upper()

assert deploy_env in ['CMBC', 'DEV', 'SPD']

env.use_ssh_config = True
if deploy_env == 'DEV':
    env.hosts = ['cmbc_dev']
if deploy_env == 'CMBC':
    env.hosts = ['cmbc_cms_prod']
if deploy_env == 'SPD':
    env.hosts = ['spd_cms']

if 'ULINE_PASSWORD' in os.environ:
    env.password = os.environ['ULINE_PASSWORD']

def deploy(host):
    host = host.upper()
    if host != 'DEV' and raw_input('Are you sure? Y/y: ').upper() != 'Y':
        sys.exit(1)

    with cd('/home/deploy/uline_api'):
        run('git checkout .')
        run('git pull')

    if host != 'DEV':
        for i in range(1, 5):
            sudo("supervisorctl restart 'uline_api:uline_api%s'" % i)
    else:
        run("supervisorctl restart uline_api")
