### Uline

#### 1. 项目结构
```
.
├── README.md
├── bin
│   └── install-ctl.sh                                                      # 部署脚本
├── etc                                                                     # 配置文件
│   ├── config.yaml
│   ├── config.yaml.template
│   └── logging.conf
├── site-packages                                                           # 第三方模块说明
│   └── requerments.txt
└── uline                                                                   # 项目根目录
    ├── __init__.py
    ├── application.py                                                      # 应用程序入口
    ├── backend                                                             # 后台执行程序
    │   └── __init__.py
    ├── handlers                                                            # 句柄
    │   ├── __init__.py
    │   ├── app
    │   │   ├── __init__.py
    │   │   └── service
    │   │       └── __init__.py
    │   └── baseHandlers.py                                                 # 基础处理句柄
    ├── log                                                                 # 日志
    │   ├── detail.lock
    │   ├── detail.log
    │   ├── exception.lock
    │   ├── exception.log
    │   ├── request.lock
    │   └── request.log
    ├── public                                                              # 公共函数
    │   ├── __init__.py
    │   ├── cbDB.py
    │   ├── cbException.py
    │   ├── cbLog.py
    │   ├── cbRedis.py
    │   ├── common.py
    │   ├── config.py
    │   └── constants.py
    ├── server.py                                                           # 服务启动
    ├── settings.py
    ├── static                                                              # 静态文件
    │   └── admin
    │       ├── css
    │       │   └── md.css
    │       ├── fonts
    │       │   ├── glyphicons-halflings-regular.eot
    │       │   └── glyphicons-halflings-regular.svg
    │       ├── img
    │       │   └── a0.jpg
    │       ├── js
    │       │   └── login.js
    │       └── libs
    │           ├── assets
    │           │   └── font-awesome
    │           │       ├── css
    │           │       │   ├── font-awesome.css
    │           │       │   └── font-awesome.min.css
    │           │       └── fonts
    │           │           ├── FontAwesome.otf
    │           │           ├── fontawesome-webfont.eot
    │           │           ├── fontawesome-webfont.svg
    │           │           ├── fontawesome-webfont.ttf
    │           │           └── fontawesome-webfont.woff
    │           └── jquery
    │               ├── bootstrap
    │                   └── dist
    │                       ├── css
    │                       │   ├── bootstrap-theme.css
    │                       │   ├── bootstrap-theme.css.map
    │                       │   ├── bootstrap-theme.min.css
    │                       │   ├── bootstrap.css
    │                       │   ├── bootstrap.css.map
    │                       │   └── bootstrap.min.css
    │                       ├── fonts
    │                       │   ├── glyphicons-halflings-regular.eot
    │                       │   ├── glyphicons-halflings-regular.svg
    │                       │   ├── glyphicons-halflings-regular.ttf
    │                       │   ├── glyphicons-halflings-regular.woff
    │                       │   └── glyphicons-halflings-regular.woff2
    │                       └── js
    │                           ├── bootstrap.js
    │                           ├── bootstrap.min.js
    │                           └── npm.js
    │  
    ├── templates                                                           # 模板文件
    │   ├── admin
    │   │   └── page_404.html
    │   └── error.html
    ├── test                                                                # 单元测试脚本
    │   ├── __init__.py
    │   └── unit_test.py
    ├── urls.py                                                             # 路由
    └── utils                                                               # 第三方扩展
        ├── __init__.py
        ├── rong.py
        ├── sendMsg.py
        └── yunpian.py
```

#### 2. 安装路径及配置
```
nginx安装路径：/usr/local/nginx
nginx配置文件夹： /usr/local/nginx/conf.d/
supervisor配置文件夹：/etc/supervisor.d/
logging配置文件夹：/{{project_dir}}/{{project_name}}/etc/
项目配置文件（config.yaml）：/{{project_dir}}/{{project_name}}/etc/
```

#### 3. 项目部署
```
Usage:
    sh install-ctl.sh <command> [option]
Commend:
    init
Option:
    --all
```

#### 4. 启动服务
```
启动supervisord
    /usr/bin/supervisord -c /etc/supervisor.conf
启动nginx
    /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
```

#### 5. 启动程序
```
测试环境
    python server.py --env=local
开发环境
    python server.py --env=dev
正式环境
    python server.py --env=prod
```

#### 6. 项目说明
```
清算系统
对账系统
用户资料系统
```

#### 7. alembic使用说明
```
进入uline/uline目录下
更新到最新schema: PYTHONPATH=. alembic upgrade head
自动生成更新脚本文件: PYTHONPATH=. alembic revision --autogenerate -m 'some description'
```

#### 8. 测试账号
```
mch: 100000000975
dt: ulaiber@ulaiber.com
bank: cmbchina@ulaiber.com
official: uline@ulaiber.com
```

#### 9. newrelic
```
项目使用newrelic进行性能监控
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program YOUR_COMMAND_OPTIONS
```
