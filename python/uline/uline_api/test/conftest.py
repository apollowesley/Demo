#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '11/30/16'
import pytest
from uline_api.application import Application


@pytest.fixture
def app():
    return Application()
