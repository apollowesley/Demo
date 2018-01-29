#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from uline.handlers.baseHandlers import OfclAdminHandler
from tornado.gen import coroutine
from .form import MessageSendSearch
from tornado.web import gen
from uline.public.permit import check_permission


class MessageSearchHandler(OfclAdminHandler):
    @authenticated
    @check_permission
    def prepare(self):
        self.form = MessageSendSearch(self)
        self.pageindex = int(self.get_argument("p", 1))

    @authenticated
    @coroutine
    def get(self):
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(ret[0])
        self.render('official/operations/messageSend.html', navigate_html=navigate_html, data=ret[1], form=self.form,
                    total_num=ret[0])

    @coroutine
    def db_execute(self, form, offset):
        sql = '''select id,create_at, message_content,COUNT(*) over () as total
                    from message_content_info ORDER BY id desc OFFSET %s ROWS FETCH NEXT 10 ROWS ONLY;'''
        content_list = self.db.selectSQL(sql, (offset,), fetchone=False)
        total_num = content_list[0][3]
        # 把content_list结果集中的id 和message_content做成有对应关系的dict
        content_dict = dict([[content[0], content[2]]
                             for content in content_list])
        send_id_list = [message_conent[0] for message_conent in content_list]
        detail_sql = '''
        select send_id,send_status,to_char(create_at,'YYYY-MM-DD HH24:MI:SS'), count(send_status)
            from message_send_info where send_id in %s GROUP BY  send_id,send_status,create_at;
        '''
        detail_key = ['send_id', 'send_status', 'create_at', 'send_count']
        detail_ret = self.db.selectSQL(
            detail_sql, (tuple(send_id_list),), fetchone=False)
        # 把查询结果转化为dict的list
        message_list = [dict(zip(detail_key, single)) for single in detail_ret]
        result_list = []
        for send_id in send_id_list:
            # 把结果集中包含某个send_id的内容全部找出来
            ret_list = [result for result in message_list if result.get(
                'send_id') == send_id]
            res = dict(send_id=send_id, message_conent=content_dict.get(send_id), send_success_count=0,
                       send_fail_count=0,
                       create_at=ret_list[0]['create_at'])
            for ret in ret_list:
                if ret.get('send_status') == 2:
                    need_send_count = res.get(
                        'send_success_count') + ret.get('send_count')
                    res['send_success_count'] = need_send_count
                else:
                    send_fail_count = res.get(
                        'send_fail_count') + ret.get('send_count')
                    res['send_fail_count'] = send_fail_count
            result_list.append(res)
        data_result = []
        data_result.append(total_num)
        data_result.append(result_list)
        raise gen.Return(data_result)
