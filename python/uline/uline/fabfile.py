# -*-coding:utf-8 -*-

# fab deploy:dev

import time
import sys
import os
import re
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


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


def deploy(host):
    host = host.upper()
    if host != 'DEV' and raw_input('Are you sure? Y/y: ').upper() != 'Y':
        sys.exit(1)

    # 打标签方便后面回退
    tag(host)

    with cd('/home/deploy/uline'):
        run('git checkout .')
        run('git pull')

    p = run(
        """python -c 'import os;print(int(os.stat("/home/deploy/uline/site-packages/requirements.txt").st_mtime))'""")
    if time.time() - int(p.strip()) < 24 * 3600:
        sudo(
            'pip install -r /home/deploy/uline/site-packages/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple')
    if host != 'DEV':
        sudo("supervisorctl restart celery")
        # sudo("supervisorctl restart 'uline_cms:*'")
        for i in range(1, 17):
            sudo("supervisorctl restart 'uline_cms:pyuline%s'" % i)
    else:
        run("supervisorctl restart celery")
        # run("supervisorctl restart celery 'uline_cms:*'")
        for i in range(1, 9):
            run("supervisorctl restart 'uline_cms:pyuline%s'" % i)


def tag(host):
    tag_prefix = host + '-v'
    with cd('/home/deploy/uline'):
        run("git fetch origin 'refs/tags/*:refs/tags/*'")
        tags_str = run('git tag -l %s*' % tag_prefix)
        if not ''.join(tags_str.split()):
            new_version_number = 0
        else:
            version_tags = tags_str.split('\n')
            version_tags.sort(key=natural_keys)
            last_version_tag = version_tags[-1]
            last_version_number = filter(str.isdigit, last_version_tag)
            new_version_number = int(last_version_number) + 1
        new_version_tag = tag_prefix + str(new_version_number)
        run('git tag -a %s -m deploy' % new_version_tag)
        run('git push --tags')
