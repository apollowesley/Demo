#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '16/11/1'

import sqlalchemy
import wtforms
from sqlalchemy.sql.expression import cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from uline.utils.tor import get_current_unique_id

Base = declarative_base()

trade_Session = sessionmaker()
trade_session = scoped_session(trade_Session, scopefunc=get_current_unique_id)


class CRUDMixin(object):
    """
        Mixin that adds convenience methods for CRUD
        (create, read, update, delete) operations.
    """

    @classmethod
    def create(cls, commit=False, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save(commit=commit)

    def update(self, commit=False, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=False):
        """Save the record."""
        trade_session().add(self)
        if commit:
            trade_session().commit()
        return self

    def delete(self, commit=False):
        """Remove the record from the database."""
        trade_session().delete(self)
        return commit and trade_session().commit()

    @classmethod
    def get_by(cls, commit=None, **kwargs):
        return trade_session().query(cls).filter_by(**kwargs)


class Model(CRUDMixin, Base):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    def to_dict(self, excluded=(), include=()):
        """
        将一条数据库记录转换为字典
        :param model: 数据库记录
        :param attrs_excluded: 需要过滤的字段
        :return: 返回转换后的字典
        """
        if include:
            return {c.name: getattr(self, c.name)
                    for c in self.__table__.columns if c.name in include}
        else:
            return {c.name: getattr(self, c.name)
                    for c in self.__table__.columns if c.name not in excluded}

    @classmethod
    def form_filter(cls, search_dict):
        """
        多个条件查询
        :param search_dict:
        :return:
        """

        for key, value in search_dict:
            if (not isinstance(key, (wtforms.Field, str))) and (not isinstance(value, (str, int))):
                raise Exception('key:{},value:{} must be str'.format(key, value))

        search_dict = {key.name if isinstance(key, wtforms.Field) else key: value for key, value in search_dict.items()
                       if bool(value)}

        search = [cast(getattr(cls, str(key)), sqlalchemy.String).contains(str(value)) for key, value in
                  search_dict.items()]
        return trade_session().query(cls).filter(*search)


from order import *
