# -*- coding:utf-8 -*-
import xml.dom.minidom
# https://www.cnblogs.com/AlwinXu/p/5483177.html
# print (object .__dict__)
# print (dir(object))



# IIsWebServer@ServerBindings  Location ="/LM/W3SVC/34"
# ServerBindings="211.102.91.212:80:w120615342.dodogo.cn
#			211.102.91.212:80:zhinfo.org
#			211.102.91.212:80:www.zhinfo.org"
#		ServerComment="w120615342"

# <IIsWebVirtualDir	Location ="/LM/W3SVC/11/root"
#    Path="d:\VirHost\wwwroot\w120615342" 

#import xml.dom.minidom
#>>> dom = xml.dom.minidom.parse('d:/catalog.xml')
# from xml.dom.minidom import parse


# 使用minidom解析器打开 XML 文档
DOMTree = xml.dom.minidom.parse("/Users/chenboxing1/Downloads/MetaBase.xml")
collection = DOMTree.documentElement

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
        print "%s | %s" % (comment, path)
        if path.find('\\wwwroot\\') > 0:
           print "%s | %s" % (comment, path)
        else:
           print "not in  %s | %s" % (comment, path)         
        # if path.find('\wwwroot\') > 0 :
        #     print "%s | %s" % (comment, path)
        # else:
        #     print "not in  %s | %s" % (comment, path)

                
    # if path
    #print(path)
    # print "Root element : %s %s" % (site.getAttribute("ServerComment"), site.getAttribute("ServerBindings"))