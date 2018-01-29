#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import authenticated
from uline.handlers.baseHandlers import OfclAdminHandler
from uline.public.common import f_rsp
from tornado.gen import coroutine
from tornado.web import gen
from uline.backend.official.generage_message_send_info import generate_message_send
from .form import MessageSendSearch
from uline.model.uline.base import uline_session
from uline.model.uline.info import MessageSendInfo
from uline.public.permit import check_permission


class MessageSendAddHandler(OfclAdminHandler):
    @coroutine
    @authenticated
    @check_permission
    def get(self):
        self.form = MessageSendSearch(self)
        self.pageindex = int(self.get_argument("p", 1))
        ret = yield self.db_execute(self.form, (self.pageindex - 1) * 10)
        navigate_html = self.get_navigate_html(ret[0] if ret else 0)
        self.render('official/operations/messageSend.html', navigate_html=navigate_html, data=ret[1] if ret else None,
                    total_num=ret[0] if ret else 0)

    @coroutine
    @authenticated
    @check_permission
    def post(self):
        message_content = self.get_argument("message_content", None)
        if not message_content:
            self.finish(f_rsp(406, u'短信内容不能为空'))
        banck_direct_mch_info = yield self.get_bank_direct_mch()
        if not banck_direct_mch_info:
            self.finish(f_rsp(406, u'银行直联商户为空'))
        send_id = yield self.get_send_id(message_content)
        message_send_key = ['mobile', 'mch_name', 'mch_id', 'dt_id']
        mch_list = []
        # send_status 1待发送，2已发送,3发送失败
        extend_info = dict(send_id=send_id, send_status=1,
                           message_content=message_content)
        for banck_direct_mch in banck_direct_mch_info:
            mch_info = dict(zip(message_send_key, banck_direct_mch))
            mch_info.update(extend_info)
            mch_list.append(mch_info)
        yield self.send_message_init(mch_list)
        # 新加一个app.task
        generate_message_send.delay(mch_list)
        self.finish(f_rsp(200, 'success', data=dict(send_id=send_id)))

    @coroutine
    def get_bank_direct_mch(self):
        '''
        银行直连商户的电话号码可能是重复的，SQL做了去重处理,保证同一个电话号码只发送一次短信
        '''

        query = """
                 SELECT mobile,mch_name,mch_id,dt_id from (
                     SELECT row_number() OVER(PARTITION BY mobile ORDER BY mch_id  ) row_number,mobile,mch_name,mch_id,dt_id from (
                            select mch_inlet_info.mobile,mch_inlet_info.mch_name ,mch_inlet_info.mch_id,mch_inlet_info.dt_id
                                                            from  mch_inlet_info
                                                            INNER JOIN dt_inlet_info
                                                            on  mch_inlet_info.dt_id=dt_inlet_info.dt_id
                                                            WHERE dt_inlet_info.dt_type=2
                    UNION
                            select  a.mobile , a.dt_name as mch_name,0 as mch_id,a.dt_id
                                                            from dt_inlet_info  a
                                                            INNER JOIN dt_inlet_info b
                                                            on a.parent_id=b.dt_id and b.dt_type=2) a
                    where mobile ~ '\d{11}' )tmp
                where row_number=1
                        """
        ret = self.db.selectSQL(query, fetchone=False)
        raise gen.Return(ret)

    @coroutine
    def send_message_init(self, mch_list):
        if mch_list:
            mch_tuple_list = [
                MessageSendInfo(send_id=int(mch.get('send_id')), mch_id=int(mch.get('mch_id')),
                                dt_id=int(mch.get('dt_id')), send_status=mch.get('send_status')) for mch in mch_list]
            uline_session.add_all(mch_tuple_list)
            uline_session.commit()

    @coroutine
    def get_send_id(self, message_content):
        with self.db.get_db() as cursor:
            # 在message_content插入的同时，获得id
            sql = 'insert into message_content_info(message_content) VALUES(%s) RETURNING  id'
            cursor.execute(sql, (message_content,))
        raise gen.Return(cursor.fetchone()[0])

    @coroutine
    def db_execute(self, form, offset):
        sql = '''select id,create_at, message_content,COUNT(*) over () as total
                        from message_content_info ORDER BY id desc OFFSET %s ROWS FETCH NEXT 10 ROWS ONLY;'''
        content_list = self.db.selectSQL(sql, (offset,), fetchone=False)
        if not content_list:
            raise gen.Return(None)
        total_num = content_list[0][3]
        send_id_list = [message_conent[0] for message_conent in content_list]
        detail_sql = '''
              select
                sum(CASE  WHEN message_send_info.send_status=2
                          THEN message_send_info.cout ELSE 0 end ) as sended_sucess_count,
                sum(CASE  WHEN message_send_info.send_status =3
                          or message_send_info.send_status=1
                          THEN message_send_info.cout ELSE 0 end ) as sended_fail_count,
                message_send_info.send_id,
                message_send_info.create_at,
                message_content_info.message_content
                from (select send_id,send_status,to_char(create_at,'YYYY-MM-DD HH24:MI:SS')
                        as create_at, count(send_status) as cout
                        from message_send_info
                        where send_id in %s
                        GROUP BY  send_id,send_status,create_at) message_send_info
                INNER JOIN message_content_info
                on (message_send_info.send_id= message_content_info.id)
                GROUP BY message_send_info.send_id,message_send_info.create_at,message_content_info.message_content
                ORDER BY  message_send_info.send_id DESC ;
            '''
        detail_ret = self.db.selectSQL(
            detail_sql, (tuple(send_id_list),), fetchone=False)
        data_result = []
        data_result.append(total_num)
        data_result.append(detail_ret)
        raise gen.Return(data_result)
