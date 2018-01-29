#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uline.handlers.baseHandlers import BaseHandler


class BrowserHandler(BaseHandler):
    def get(self):
        self.render("common/browser.html")