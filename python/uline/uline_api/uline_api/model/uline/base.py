#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '16/11/1'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from uline_api.util.tor import get_current_request_id

Base = declarative_base()

uline_Session = sessionmaker()
uline_session = scoped_session(uline_Session, scopefunc=get_current_request_id)


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
        uline_session().add(self)
        if commit:
            uline_session().commit()
        return self

    def delete(self, commit=False):
        """Remove the record from the database."""
        uline_session().delete(self)
        return commit and uline_session().commit()

    @classmethod
    def get_by(cls, commit=None, **kwargs):
        return uline_session().query(cls).filter_by(**kwargs)


class Model(CRUDMixin, Base):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    def to_dict(self, columns=(), excluded=True):
        """
        将一条数据库记录转换为字典
        :param model: 数据库记录
        :param attrs_excluded: 需要过滤的字段
        :return: 返回转换后的字典
        """
        if not excluded:
            return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in columns}

        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns if c.name not in columns}


from clear import *
from other import *
from error import *
from info import *
from user import *
from balance import *
