# -*- coding: UTF-8 -*-
import MySQLdb

# 打开数据库连接
db = MySQLdb.connect("211.102.90.92","move8.cn","lovemay1314","move8_cn")

# 使用cursor()方法获取操作游标 
cursor = db.cursor()

# SQL 查询语句
sql = "SELECT * FROM poral_users limit 10"
try:
   # 执行SQL语句
   cursor.execute(sql)
   # 获取所有记录列表
   results = cursor.fetchall()
   for row in results:
       
      print row  
      
      fname = row[0]
      lname = row[1]
      age = row[2]
      sex = row[3]
      income = row[4]

      # 打印结果
      print "fname=%s,lname=%s,age=%d,sex=%s,income=%d" % \
             (fname, lname, age, sex, income )
except:
   print "Error: unable to fecth data"
