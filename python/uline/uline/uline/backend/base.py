# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
from celery import platforms
from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from uline.model.uline.base import Model as uline_Model, uline_Session
from uline.backend.common import *
from uline.backend.config import CELERY_RESULT_DBURI

reload(sys)
sys.setdefaultencoding('utf-8')

platforms.C_FORCE_ROOT = True


def get_session(uri=CELERY_RESULT_DBURI):
    uline_engine = create_engine(uri, pool_recycle=3600)
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=uline_engine))
    return session


class BaseTask(Task):
    abstract = True
    _uline_session = None
    _trade_session = None

    def after_return(self, *args, **kwargs):
        if self._uline_session:
            self._uline_session.remove()

    @property
    def uline_session(self):
        if not self._uline_session:
            session = get_session()
            self._uline_session = session
        return self._uline_session
