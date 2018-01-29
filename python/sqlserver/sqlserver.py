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

# w100921267
# H.HostName, U.Mobile, U.Email, U.DisplayName, U.Province, U.Address, U.City, G.ProductName, 
# G.BeginDate, G.EndDate From Main_HostList H Main_Goods G, Main_Users U  where H.GoodsNo = G.GoodsNO 
# And H.="" And G.UserID = U.UseriD
sql = """
    SELECT H.HostName, U.Mobile, U.Email, U.DisplayName, U.Province, U.Address, U.City, G.ProductName, 
    G.BeginDate, G.EndDate From Main_Goods G inner join Main_HostList H  on H.GoodsNo = G.GoodsNO 
    left join Main_User U on G.UserID = U.UserID where H.HostName = 'w100921267'
"""

reslist = ms.ExecQuery(sql)
for i in reslist:
    # chardet.detect(i[1])
    # encode('latin1').decode('gbk')
    str1 = "" 
    for k in i:
        print k
        

    

    # print i[1]
    # print i[1].encode('latin1').decode('gbk')
    # print i

# newsql = "update webuser set name='%s' where id=1" % u'测试'
# print newsql
# ms.ExecNonQuery(newsql.encode('utf-8'))
