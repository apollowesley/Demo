#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Liufei
# Create: '17/8/17'

from tornado.web import URLSpec as url
from .role_controller import RoleController
# from .user_role_controller import UserRoleController
# from .model_controller import ModelController
from .permit_controller import PermitController
from .have_permit_controller import HavePermitController
# from .structure_controller import StructureController


# 前缀common/permit
urls = [
    url(r'/role', RoleController),
    # url(r'/user', UserRoleController),
    # url(r'/model', ModelController),
    # url(r'/permit', PermitController),
    # url(r'/have_permission', HavePermitController)
    # url(r'/structure', StructureController),
]
