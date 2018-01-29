
## 0.1.0[2017.3.6]
----

* 引入pre-commit增强代码质量
* 开始将短信和邮件分离,将spd_master分支和mcbc_master分支合并
* 将配置文件统一
* 本地开发环境可以使用reset_pwd.py文件重置所有密码,方便测试登陆

## 0.1.1[2017.3.14]
--
* 合并初步完成,将环境及配置统一,短信和邮件使用uline_message项目使用docker运行
* `问题`: 暂时将supervisord的celery使用root权限运行
* 添加dev_util目录,方便大家同步测试环境数据到本地
* 添加webhook触发,push到stage的时候自动重启测试环境程序