丢丢环保Python上传小工具，将Excel文件小区用户记录上传至指定的MySQL数据表.

### 使用指南
1. 需要先在丢丢环保后台添加小区记录,并获取小区ID号。
2. Excel文件的命名格式为area_33_xxxx.xls (其中33为小区ID号),Excel的文件类型只能为xls.
3. 将要上传的Excel文件放置在upload目录里，如文件上传成功，会移至done目录。
4. Excel文件的内容模板参数templete.xls.
5. 在配置文件log.conf里配置好MySQL数据库信息，执行./main.py，按提示输入正确的MySQL帐号密码.

### 目录文件说明

done/      存放操作成功的Excel文件
log/       存放日志文件
upload/    要上传的Excel目录要放置此目录
log.conf   日志配置文件
main.py    主文件
upload_task Excel文件操作记录上传实际逻辑
template.xlsx Excel模板文件参考

### 第三方库
工具中所使用下面第三方库
xlrd         Excel操作
MySQLdb      MySQL操作

pip install xlrd
pip install mysql-python

为MySQL 的Python驱动接口包，可以到http://sourceforge.net/projects/mysql-python/下载安装。在Ubuntu值哦你可以使用sudo apt-get install python-mysql,
centos使用sudo yum install python-mysql安装