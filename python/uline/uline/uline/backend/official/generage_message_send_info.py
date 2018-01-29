# -*- coding: utf-8 -*-
from __future__ import division

from uline.backend.__init__ import *
from tornado.httpclient import HTTPClient
from uline.settings import env, MESSAGE_URL
import json
from tornado.web import HTTPError
from uline.public import log


@app.task
def generate_message_send(mch_list):
    with db.get_db() as cusor:
        for mch in mch_list:
            mobile = mch.get('mobile')
            http_client = HTTPClient()
            data = {
                'env': env,
                'reciver': mobile,
                'body': mch.get('message_content')
            }
            url = MESSAGE_URL + '/v1/message'
            send_status = 3
            try:
                log.exception.info(data)
                response = http_client.fetch(
                    url, method='POST', body=json.dumps(data))
                log.exception.info("str(response.body):" + str(response.body))
                if str(response.body) == '2':
                    send_status = 2
            except HTTPError as err:
                log.exception.exception(err)
            log.exception.info("str(send_status):" + str(send_status))
            update_message_send_status(
                cusor, send_status, mch.get('send_id'), mch.get('mch_id'))


def update_message_send_status(cur, send_status, send_id, mch_id):
    sql = "UPDATE  message_send_info SET send_status=%s,send_at=now() WHERE send_id=%s AND mch_id=%s;"
    cur.execute(sql, (send_status, send_id, mch_id))
