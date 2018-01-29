#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ficapy
# Create: '10/8/16'

from tornado.web import URLSpec as url

from .mchs_email_send import (
    ShowGatherEmailSend, ResendEmail

)

# 前缀dist/settings/
urls = [
    url(r'email', ShowGatherEmailSend),
    url(r'resend_email', ResendEmail),


]
