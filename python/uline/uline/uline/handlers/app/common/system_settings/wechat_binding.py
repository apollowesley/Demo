# -*- coding: utf-8 -*-
import hashlib
import json
from uline.settings import auth_access_token
import xmltodict
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from uline.public import common, log
from uline.handlers.baseHandlers import CommanHandler
from uline.model.uline.base import uline_session
from .sub_user_form import GenerateQrcode, BindingStatus
from .common import get_access_token, get_user_profile, get_employee_login
from uline.model.uline.info import UserProfile, MchInletInfo
from uline.model.uline.user import Employee
from tornado.web import authenticated


# 获取临时二维码


class WebChat(CommanHandler):

    @authenticated
    def prepare(self):

        self.form = GenerateQrcode(self)
        self.employee_id = self.form.employee_id.data

    @gen.coroutine
    def get(self):

        if not self.form.validate():
            self.write(common.f_rsp(msg=(self.form.errors)['employee_id']))
            return

        query = get_user_profile(self.employee_id)
        if query.status != 1:
            rsp = common.f_rsp(code=406, msg='该员工处于禁用状态,暂不能绑定微信,请启用后再尝试')
        else:
            try:
                for i in range(3):
                    access_token = yield get_access_token(self.rdb, refresh=bool(i != 0))
                    ticket = yield self.get_ticket(access_token)
                    if ticket != "err_ticket":
                        break
                else:
                    rsp = common.f_rsp(code=406, msg='获取二维码失败,请刷新重试')
                    self.write(rsp)
                    return

                qr_scan_url = u"https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=%s" % (
                    ticket)
                rsp = common.f_rsp(code=200, msg='success',
                                   scan_url=qr_scan_url)
                self.write(rsp)
                return

            except Exception as e:
                log.exception.exception(e)
                rsp = common.f_rsp(code=406, msg='获取二维码失败,请刷新重试')
        self.write(rsp)
        return

    @gen.coroutine
    def get_ticket(self, access_token):
        scene_id = int(self.employee_id) + 123
        body = {"expire_seconds": 604800, "action_name": "QR_SCENE",
                "action_info": {"scene": {"scene_id": scene_id}}}
        jsons = json.dumps(body)
        ticket = "err_ticket"
        try:
            url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s" % (
                access_token)
            response = yield AsyncHTTPClient().fetch(url, method='POST', body=jsons)
            result_string = json.loads(response.body)
            if result_string.get('ticket', "err_ticket") != "err_ticket":
                ticket = result_string['ticket']
        except Exception as e:
            log.exception.exception(e)
        raise gen.Return(ticket)


class Getbindingstatus(CommanHandler):
    # 反馈绑定或者解绑状态

    def prepare(self):
        form = BindingStatus(self)
        if not form.validate():
            response = common.f_rsp(code=406, msg='无效参数')
            self.write(json.dumps(response))
            self.finish()
            return
        self.employee_id = self.get_argument('employee_id')
        self.binding_status = self.get_argument("binding_status")  # 1为绑定,2为解绑

    def get(self):
        employee_id = get_employee_login(self.employee_id)
        try:
            msg = {"code": 406, "msg": "操作失败,请重新尝试!"}
            if self.binding_status == u'1':
                query = get_user_profile(self.employee_id)
                if query.wx_id and query.wx_open_id:
                    msg = {"code": 200, "msg": 1}  # 1 为绑定成功,2 为解绑成功
                else:
                    msg = {"code": 200, "msg": ""}
            elif self.binding_status == u'2':
                uline_session.query(UserProfile.wx_open_id, UserProfile.wx_id).filter(
                    UserProfile.id == employee_id.user_id).update({"wx_id": None, "wx_open_id": None})
                uline_session.commit()
                msg = {"code": 200, "msg": 2}
        except Exception as err:
            log.exception.exception(err)
            msg = {"code": 406, "msg": "操作失败,请重新尝试!"}
        self.write(msg)
        return
