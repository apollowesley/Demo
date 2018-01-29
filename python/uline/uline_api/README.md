=======
## Readme

该项目本地测试请使用招商银行测试环境的数据,导出到本地后进行导入再测试,测试的渠道商id为10000000830,key为7290C9989626D3D78496CA831FDAB3CC
Authorization为  MTAwMDAwMDA4MzA6NzI5MEM5OTg5NjI2RDNENzg0OTZDQTgzMUZEQUIzQ0M=

招商银行测试环境域名: http://pay.stage.uline.cc
招行正式域名: http://ulineapi.cms.cmbxm.mbcloud.com
浦发正式域名: https://dtapi.spd.uline.cc

```
使用acme.sh配置SSL,建议先切换到root权限下再执行操作(因为用普通权限的时候使用sudo nginx restart需要密码,不利于自动化操作)
```

## acme.sh使用

1. 安装

    ```
    curl https://get.acme.sh | sh
    ```
2. 配置阿里云dns的api

    ```
    export Ali_Key="xxxxxxxxxxxx"
    export Ali_Secret="xxxxxxxxxxxx"
    ```
2. 使用

    ```
    # pay.spd  cms.spd apichef.spd sa.spd dtapi.spd
    acme.sh --issue --dns dns_ali -d dtapi.spd.uline.cc -d pay.spd.uline.cc -d cms.spd.uline.cc -d apichef.spd.uline.cc -d api.mch.spd.uline.cc --debug
    ```

3. 设置自动化重启命令

    ```
    acme.sh --installcert -d dtapi.spd.uline.cc \
           --keypath       /etc/nginx/ssl/dtapi.spd.uline.cc.key  \
           --fullchainpath /etc/nginx/ssl/dtapi.spd.uline.cc.pem \
           --reloadcmd     "sudo service nginx force-reload"
    ```

4. 生成文件dhparam文件

    ```
    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
    ```

5. 添加Nginx配置文件

    ```
    upstream dtapi{
    	server	127.0.0.1:9901;
    }
    server {
        listen  80;
        listen  443 ssl;
        server_name  dtapi.spd.uline.cc;

        ssl_certificate /etc/nginx/ssl/dtapi.spd.uline.cc.pem;
        ssl_certificate_key /etc/nginx/ssl/dtapi.spd.uline.cc.key;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;


        # Diffie-Hellman parameter for DHE ciphersuites, recommended 2048 bits
        ssl_dhparam /etc/nginx/ssl/dhparam.pem;

        # intermediate configuration. tweak to your needs.
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers 'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS';
        ssl_prefer_server_ciphers on;


        location / {
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_read_timeout 300;
            proxy_pass http://dtapi;
        }

        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   /usr/share/nginx/html;
        }

    }
    ```

