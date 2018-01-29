#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public.common import f_rsp
from tornado.gen import coroutine
from tornado.web import gen
from uline.public.permit import check_permission


class MessageSendSerchByIdHandler(OfclAdminHandler):
    @coroutine
    @authenticated
    @check_permission
    def get(self):
        send_id = self.get_argument("send_id", None)
        if not send_id:
            self.finish(f_rsp(406, u'send_id不能为空'))
        message_info_list = yield self.get_messagecount_info(send_id)
        if not message_info_list:
            self.finish(f_rsp(406, u'send_id:{}查找到的记录为空，请确认').format(send_id))
        message_info_key = ['send_id', 'send_status', 'status_count']
        message_result = [dict(zip(message_info_key, message_info))
                          for message_info in message_info_list]
        sended_count = need_send_count = 0
        for message in message_result:
            if message.get('send_status') == 1:
                need_send_count = message.get('status_count')
            else:
                sended_count += message.get('status_count')
        data = dict(send_id=send_id, sended_count=sended_count,
                    need_send_count=need_send_count)
        self.finish(f_rsp(200, msg='success', data=data))

    @coroutine
    def get_messagecount_info(self, send_id):
        query = """
            select send_id,send_status,count(send_status)
            from message_send_info where send_id =%s GROUP BY  send_id,send_status;
        """
        ret = self.db.selectSQL(query, (send_id,), fetchone=False)
        raise gen.Return(ret or None)
