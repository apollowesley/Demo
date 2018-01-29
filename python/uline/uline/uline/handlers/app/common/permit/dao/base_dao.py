#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Liufei
# Create: '17/8/17'

from uline.public import log
from uline.public.baseDB import DbClient
from uline.public.baseTradeDB import TradeDbClient
from uline.handlers.app.common.message import Message
# from uline.model.uline.base import uline_session


class BaseDao:
    def __init__(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()

    def create(self, model, uline_session=None, commit=True, return_datas=None):
        """
        创建一条记录
        :param model: 具体操作的哪个实体对象
        :param commit: 是否提交
        :param args:
        :param kwargs:
        :return: False 代表失败 True 代表成功
        """
        message = Message()
        try:
            uline_session.add(model)
            if commit:
                uline_session.commit()
                if return_datas:
                    # 返回刚刚添加的一些数据
                    for return_data in return_datas:
                        message.SUCCESS['data'][return_data] = getattr(model, return_data, "")
                uline_session.close()
            return message.SUCCESS
        except Exception as err:
            log.exception.info(err)
            return message.CREATE_ERROR

    def update(self, Model, update_datas, where_fields, uline_session=None, commit=True):
        """
        更新一条记录
        uline_session.query(RoleInfo).filter(RoleInfo.role_id == '5').update({RoleInfo.role_name: "圣骑士", RoleInfo.create_user: "教皇"}, synchronize_session=False)
        :param Model: 具体操作的哪个实体类
        :param update_datas: 按照ORM拼装好的update格式数据，是一个字典
        :param where_fields: ORM格式的更新条件，是一个list
        :param args:
        :param kwargs:
        :return: False 代表失败 True 代表成功
        """
        message = Message()
        try:
            result = uline_session.query(Model).filter(*where_fields).update(update_datas, synchronize_session=False)
            if commit:
                uline_session.commit()
                uline_session.close()
            if result <= 0:
                return message.NOT_FOUND
            return message.SUCCESS
        except Exception as err:
            log.exception.info(err)
            return message.UPDATE_ERROR

    def delete(self, Model, where_fields, uline_session=None, commit=True):
        """
        删除一条记录
        :param args:
        :param kwargs:
        :return: False 代表失败 True 代表成功
        """
        message = Message()
        try:
            result = uline_session.query(Model).filter(*where_fields).delete(synchronize_session=False)
            if commit:
                uline_session.commit()
                uline_session.close()
            if result <= 0:
                return message.NOT_FOUND
            return message.SUCCESS
        except Exception as err:
            log.exception.info(err)
            return message.DELETE_ERROR

    def find(self, select_fields, where_fields, uline_session=None, commit=True):
        """
        查询一条记录
        :param args:
        :param kwargs:
        :return: 返回的是数据库字段和值对应的dict
        """
        message = Message()
        try:
            result = {}
            model = uline_session.query(*select_fields).filter(*where_fields).first()
            if not model:
                return message.NOT_FOUND
            for field in model._fields:
                result[field] = getattr(model, field)
            if commit:
                uline_session.commit()
                uline_session.close()
            message.SUCCESS["data"] =result
            return message.SUCCESS
        except Exception as err:
            log.exception.info(err)
            return message.QUERY_ERROR

    def find_all(self, select_fields, uline_session=None, where_fields=None, commit=True):
        """
        查询多条记录
        :param args:
        :param kwargs:
        :return: 返回是一个list，list里面是多个dict(和find方法的返回值格式一样)
        """
        message = Message()
        try:
            models = uline_session.query(*select_fields).filter(*where_fields).all()
            if not models:
                return message.NOT_FOUND
            for model in models:
                result = {}
                for field in model._fields:
                    result[field] = getattr(model, field)
                message.MORE_SUCCESS["data"].append(result)
            if commit:
                uline_session.commit()
                uline_session.close()
            return message.MORE_SUCCESS
        except Exception as err:
            log.exception.info(err)
            return message.QUERY_ERROR

    def find_more(self, select_fields, where_fields, order_fields, uline_session=None, commit=True, page_index=1, page_size=10):
        """
        查询多条记录
        :param args:
        :param kwargs:
        :return: 返回是一个list，list里面是多个dict(和find方法的返回值格式一样)
        """
        message = Message()
        try:
            offset = (page_index - 1) * page_size
            models = uline_session.query(*select_fields).filter(*where_fields).order_by(*order_fields).offset(offset).limit(
                page_size).all()
            if not models:
                return message.NOT_FOUND
            for model in models:
                result = {}
                for field in model._fields:
                    result[field] = getattr(model, field)
                message.MORE_SUCCESS["data"].append(result)
            if commit:
                uline_session.commit()
                uline_session.close()
            return message.MORE_SUCCESS
        except Exception as err:
            log.exception.info(err)
            return message.QUERY_ERROR
