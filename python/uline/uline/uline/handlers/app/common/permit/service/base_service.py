#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Liufei
# Create: '17/8/17'

from uline.handlers.app.common.permit.dao.base_dao import BaseDao
from uline.model.uline.base import uline_session


class PermitService:

    def __init__(self):
        self.dao = BaseDao()

    def create(self, Model, form_datas, return_datas=None):
        model = Model()
        for field_key in form_datas:
            model.__setattr__(field_key, form_datas.get(field_key))
        return self.dao.create(model, uline_session, return_datas=return_datas)

    def find(self, Model, query_fields, form_datas):
        """
        查询方法
        :param Model: 需要查询哪个实体类
        :param query_fields: 需要查询哪些字段，是一个list
        :param form_datas: 查询所需要的key 和 value 是一个 dict
        :return: query_fields字段作为key，查询结果作为value封装在Message类中返回json格式数据
        """

        # ORM操作数据库需要的数据格式
        where_fields = list()
        select_fields = list()

        # 需要查询的字段 select 后的字段
        for query_field in query_fields:
            select_fields.append(getattr(Model, query_field))

        # 查询需要的条件 where 后的字段
        for form_data in form_datas:
            model_data = getattr(Model, form_data, None)
            if model_data:
                where_fields.append(getattr(Model, form_data) == form_datas.get(form_data))

        return self.dao.find(select_fields, where_fields, uline_session)

    def find_more(self, Model, query_fields, form_datas, order_fields=None, page_index=1, page_size=10):
        where_fields = list()
        select_fields = list()

        # 需要查询的字段 select 后的字段
        for query_field in query_fields:
            select_fields.append(getattr(Model, query_field))

        # 查询需要的条件 where 后的字段
        for form_data in form_datas:
            model_data = getattr(Model, form_data, None)
            if model_data:
                where_fields.append(getattr(Model, form_data) == form_datas.get(form_data))

        db_order_fields = list()
        for order_field in order_fields:
            db_order_fields.append(getattr(Model, order_field))

        return self.dao.find_more(select_fields, where_fields, db_order_fields,
                                  uline_session, page_index=page_index, page_size=page_size)

    def find_all(self, Model, query_fields):
        select_fields = list()
        for query_field in query_fields:
            select_fields.append(getattr(Model, query_field))
            return self.dao.find_all(select_fields, uline_session)


    def patch(self, Model, filter_fields, update_fields, form_datas):
        """
        更新一条记录
        :param Model: 需要更新哪个实体类
        :param filter_fields: 更新过滤条件
        :param update_fields: 需要更新的字段
        :param form_datas: 数据json
        :return:
        """
        update_datas = {}
        where_fields = list()

        # 需要更新那些字段
        for update_field in update_fields:
            update_datas[getattr(Model, update_field)] = form_datas.get(update_field)

        # 更新这些字段的过滤是什么
        for filter_field in filter_fields:
            where_fields.append(getattr(Model, filter_field) == form_datas.get(filter_field))

        return self.dao.update(Model, update_datas, where_fields, uline_session)

    def delete(self, Model, filter_fields, form_datas):
        where_fields = list()

        # 删除条件
        for filter_field in filter_fields:
            where_fields.append(getattr(Model, filter_field) == form_datas.get(filter_field))

        return self.dao.delete(Model, where_fields, uline_session)
