#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/4/16'
from sqlalchemy import Column, DateTime, Integer, String, SmallInteger, Sequence, Index

from .base import Model as Base


class ReconRefundErrorInfo(Base):
    __tablename__ = 'recon_refund_error_info'

    id = Column(Integer, Sequence('recon_refund_error_info_id_seq', metadata=Base.metadata),
                primary_key=True)
    out_refund_no = Column(String(64), nullable=False)
    detail = Column(String(2048), nullable=False)
    handle_status = Column(SmallInteger, nullable=False)
    except_type = Column(SmallInteger, nullable=False)
    description = Column(String(2048))
    create_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('recon_refund_error_info_id_uindex', id, unique=True),
    )


class ReconTxErrorInfo(Base):
    __tablename__ = 'recon_tx_error_info'

    id = Column(Integer, Sequence('recon_tx_error_info_id_seq'), primary_key=True)
    out_trade_no = Column(String(64), nullable=False)
    detail = Column(String(2048), nullable=False)
    handle_status = Column(SmallInteger, nullable=False)
    except_type = Column(SmallInteger, nullable=False)
    description = Column(String(64))
    create_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('recon_tx_error_info_id_uindex', id, unique=True),
    )
