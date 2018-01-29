# -*- coding: utf-8 -*-

socket_host = '10.19.2.39'
sock_port = '6666'


def unicode_to_gbk(msg):
    return msg.encode('gbk', 'ignore')


def xml_to_send(xml):
    message = unicode_to_gbk(xml)
    message = '{:0>10}'.format(len(message)) + message
    message = message.decode('GBK')
    return message
