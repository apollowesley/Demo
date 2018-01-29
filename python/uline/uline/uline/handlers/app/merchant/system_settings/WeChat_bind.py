# -*- coding: utf-8 -*-
from uline.settings import auth_access_token
from uline.model.uline.user import Employee
from uline.handlers.baseHandlers import CommanHandler
import hashlib
import xmltodict
from tornado import gen
from uline.model.uline.base import uline_session
from uline.model.uline.info import UserProfile
from tornado.httpclient import AsyncHTTPClient
from uline.public import log
from uline.handlers.app.common.system_settings.common import get_access_token, get_employee_login
import json


class GetOpenid(CommanHandler):

    def prepare(self):
        self.data = self.request.body

    def get(self):
        signature = self.get_argument('signature')
        timestamp = self.get_argument('timestamp')
        nonce = self.get_argument('nonce')
        token = auth_access_token
        echostr = self.get_argument('echostr')
        list = [token, timestamp, nonce]
        list.sort()
        list2 = ''.join(list)
        sha1 = hashlib.sha1()
        sha1.update(list2.encode('utf-8'))
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            self.write(echostr)
            return

    @gen.coroutine
    def post(self):
        self.finish('success')
        parse_xml = xmltodict.parse(self.data).get('xml')
        openid, _scene_id, event = parse_xml.get('FromUserName'), \
            parse_xml.get('EventKey', None), \
            parse_xml.get('Event')

        if event == "unsubscribe":
            uline_session.query(UserProfile.wx_open_id, UserProfile.wx_id).filter(
                UserProfile.wx_open_id == openid).update({"wx_open_id": None, "wx_id": None})
            uline_session.commit()
        elif event in ["SCAN", "subscribe"]:
            scene_auth, user_id = self.auth_scene_id(_scene_id)
            if not scene_auth:
                return
            for i in range(3):
                access_token = yield get_access_token(self.rdb, refresh=bool(i != 0))
                result = yield self.get_employee_detail(access_token, openid, user_id, event)
                if result == 2:
                    break
        return

    @gen.coroutine
    def get_employee_detail(self, access_token, openid, user_id, event):

        url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN' \
            .format(access_token, openid)
        response = yield AsyncHTTPClient().fetch(url)
        data = json.loads(response.body)
        if data.get('errcode', 'error') != 'error':
            result = 1
        else:
            try:
                uline_session.query(UserProfile.wx_open_id, UserProfile.wx_id).filter(
                    UserProfile.id == user_id).update(
                    {"wx_id": data['nickname'], "wx_open_id": openid})
                uline_session.commit()
                result = 2
            except Exception as err:
                uline_session.rollback()
                log.exception.exception(err)
                result = 1
        raise gen.Return(result)

    def check_xsrf_cookie(self):
        pass

    def auth_scene_id(self, scene_id):
        auth, user_id = True, ""
        if not scene_id:
            auth = False
        else:
            _scene_id = scene_id[8:] if scene_id.startswith('qrscene_') else scene_id
            if not _scene_id.isdigit():
                auth = False
            if auth:
                employee = get_employee_login((int(_scene_id) - 123))
                auth = True if employee else False
                user_id = employee.id if auth else ""
        return [auth, user_id]
