# -*- coding: utf-8 -*-
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


tree = ET.parse('return.xml')
root = tree.getroot()
print root.find('errcode').text
print root.find('errmess').text
print root.find('sessionID').text
print root.find('msgNo').text
