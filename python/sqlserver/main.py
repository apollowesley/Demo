# -*- coding:utf-8 -*-

import sqlserver
import csv
import sys

import codecs 


def getSiteInfo(siteList,bind_domains):

    sites = ["'" + x + "'" for x in siteList]
    sqlIn = ",".join(sites)
    ms = sqlserver.MSSQL(host="211.102.91.212", user="DaysPortal",
           pwd="pass@word1", db="DaysNetPortal")

    sql = """
        SELECT H.HostName, U.Mobile, U.Email, U.DisplayName, U.Province, U.Address, U.City, G.ProductName, 
        G.BeginDate, G.EndDate From Main_Goods G inner join Main_HostList H  on H.GoodsNo = G.GoodsNO 
        left join Main_User U on G.UserID = U.UserID where H.HostName in (%s)
    """
    sqlTxt = sql % sqlIn

    print sqlTxt
    reslist = ms.ExecQuery(sqlTxt)

    
    infos = []

    for row in reslist:
        # chardet.detect(i[1])
        # encode('latin1').decode('gbk')

        domain = ""
        if row[0] in bind_domains:
            domain = bind_domains[row[0]]

        print row[8].strftime('%Y-%m-%d')

        mobile = row[1]
        if not mobile:
            mobile = ""

        email = row[2]
        if not email:
            email = ""

        province = row[4]
        if not province:
            province = ""

        address = row[5]
        if not address:
            address = ""

        city = row[6]
        if not city:
            city = ""                

        info = {
            "HostName": row[0],
            "Mobile": mobile,
            "Email": email,
            "DisplayName": row[3],
            "Province": province,
            "Address": address,
            "City": city,
            "ProductName": row[7],
            "BeginDate": row[8].strftime('%Y-%m-%d'),
            "EndDate": row[9].strftime('%Y-%m-%d'),
            "Domain": domain
        }

        infos.append(info)

    return infos 


def writeToCsv(sites, csvFile):
    header = ["主机名", "产品名称", "域名", "用户", "联系方式","开始时间","结束时间"]

    #open('文件名','wt',encoding='gbk')搜索
    with codecs.open(csvFile,"wb",encoding='gbk') as f:
    #with open(csvFile, 'wb', encoding='gbk') as f:      # 采用b的方式处理可以省去很多问题
        
        writer = csv.writer(f)

        #writer.writerows(someiterable)

        # Header
        writer.writerow(header)

        for site in sites:
            contact = site["Mobile"] + " " + site["Email"] + site["Province"] + site["City"] + site["Address"]
            #contact = site["Mobile"]
            row = [site["HostName"], site["Domain"], site["ProductName"], site["DisplayName"], contact,site["BeginDate"], site["EndDate"]]

            print row 
            writer.writerow(row)


def getIISSiteList(metaBaseXml):
    """从metabase Xml配置文件读取网站列表"""
    # "/Users/chenboxing1/Downloads/MetaBase.xml"
    import xml.dom.minidom
    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parse(metaBaseXml)
    collection = DOMTree.documentElement

    siteList = []
    domainBinds = {}

    hashRoot = {}
    siteroots = collection.getElementsByTagName("IIsWebVirtualDir")
    for root in siteroots:
        hashRoot[root.getAttribute("Location")] =  root.getAttribute("Path")
        #print "%s %s" % (root.getAttribute("Location"), root.getAttribute("Path"))

    sites = collection.getElementsByTagName("IIsWebServer")
    for site in sites:
        comment = site.getAttribute("ServerComment")
        location = site.getAttribute("Location")
        
        if location + "/root" in hashRoot:        
            path = hashRoot[location + "/root"]
            #print "%s | %s" % (comment, path)
            if path.find('\\wwwroot\\') > 0:
               
                bindings = site.getAttribute("ServerBindings")
                domains = []
                for item in  bindings.split():
                    domains.append(item.split(":")[2])

                domainBinds[comment]=",".join(domains)
                siteList.append(comment,)
                #print "%s | %s" % (comment, path)            

    return siteList, domainBinds


def main():

    reload(sys)
    sys.setdefaultencoding('utf-8')

    siteList,domains = getIISSiteList("/Users/chenboxing1/Downloads/MetaBase.xml")    
    infos = getSiteInfo(siteList,domains)
    writeToCsv(infos, "/Users/chenboxing1/Downloads/47_88_3_109.csv")
    
if __name__ == "__main__":
    main()