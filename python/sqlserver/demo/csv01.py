# -*- coding:utf-8 -*-
import csv

datas = [['陈三', '36822@sf.com'],
         ['张四', 'asdfasdf@cccc.com']]

header = ["用户名", "Email"]

with open('/Users/chenboxing1/Demo/python/sqlserver/data/1.csv', 'wb') as f:      # 采用b的方式处理可以省去很多问题
    writer = csv.writer(f)
    #writer.writerows(someiterable)

    # Header
    writer.writerow(header)

    for row in datas:
        writer.writerow(row)



