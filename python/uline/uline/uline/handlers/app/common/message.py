#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Liufei
# Create: '21/9/17'


class Message:
    """
        消息实体类
    """
    def __init__(self):
        self.SUCCESS = {
            "code": 200,
            "msg": u"成功",
            "data": {}
        }

        self.MORE_SUCCESS = {
            "code": 200,
            "msg": u"成功",
            "data": []
        }

        self.ERROR = {
            "code": 700
        }

        self.NOT_VISIT = {
            "code": 999,
            "msg": u"无权限访问，请联系管理员"
        }

        self.CODE_ERROR = {
            "code": 10000,
            "msg": u"程序错误，请联系管理员"
        }

        self.PARAMETER_COUNT_ERROR = {
            "code": 10001,
            "msg": u"参数错误：{0} 是必填字段"
        }

        self.PARAMETER_LEN_ERROR = {
            "code": 10002,
            "msg": u"参数错误：{0} 限制为 {1} 个字符"
        }

        self.PARAMETER_DATA_ERROR = {
            "code": 10003,
            "msg": u"无效的数据类型：{0}"
        }

        self.PARAMETER_SMALL_INT_LEN_ERROR = {
            "code": 10004,
            "msg": u"超出最大长度限制"
        }

        self.PAGE_NUM_ERROR = {
            "code": 10005,
            "msg": u"分页数据不符合条件"
        }

        self.JSON_ERROR = {
            "code": 20001,
            "msg": u"无效的数据格式"
        }

        self.NUMBER_TYPE_ERROR = {
            "code": 30001,
            "msg": u"{0} 不是一个有效的数字"
        }

        self.CREATE_ERROR = {
            "code": 50001,
            "msg": u"保存失败"
        }

        self.UPDATE_ERROR = {
            "code": 50002,
            "msg": u"更新失败"
        }

        self.DELETE_ERROR = {
            "code": 50003,
            "msg": u"删除失败"
        }

        self.QUERY_ERROR = {
            "code": 50004,
            "msg": u"查询失败"
        }

        self.NOT_FOUND = {
            "code": 50005,
            "msg": u"查询记录不存在"
        }

        self.NO_PERMIT = {
            "code": 60001,
            "msg": u"权限超出范围"
        }
