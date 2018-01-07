# -*- coding:utf-8 -*-

# Server=(local);Database=DaysNetPortal;uid=DaysPortal;pwd=pass@word1

import pymssql


class MSSQL:
    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise(NameError, "没有设置数据库信息")
        self.conn = pymssql.connect(
            host=self.host, user=self.user, password=self.pwd, database=self.db, charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError, "连接数据库失败")
        else:
            return cur

    def ExecQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        # 查询完毕后必须关闭连接
        self.conn.close()
        return resList

    def ExecNonQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()


ms = MSSQL(host="211.102.91.212", user="DaysPortal",
           pwd="pass@word1", db="DaysNetPortal")
reslist = ms.ExecQuery("select top 5 *  from Main_Product")
for i in reslist:
    # chardet.detect(i[1])
    # encode('latin1').decode('gbk')
    for k in i:
        print k

    # print i[1]
    # print i[1].encode('latin1').decode('gbk')
    # print i

# newsql = "update webuser set name='%s' where id=1" % u'测试'
# print newsql
# ms.ExecNonQuery(newsql.encode('utf-8'))
