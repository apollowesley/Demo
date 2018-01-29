# -*- coding: utf-8 -*-
import hashlib
import json
from datetime import timedelta
from datetime import datetime
from uline.settings import auth_access_token
import xmltodict
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous
from uline.public import common, log

from uline.handlers.baseHandlers import MchAdminHandler
from uline.settings import QR_SCAN_URL

from uline.model.uline.user import MchSubUser, MchUserMchSubUser
from uline.model.uline.base import uline_session

from .sub_user_form import SubUserIndexForm, SubUserAddForm, SubUserInfoForm, SubUserEditForm, GenerateQrcode
from uline.public.permit import check_permission

INDEX_PAGE_SIZE = 10


class SubUserSearchHandler(MchAdminHandler):
    """处理查询子账户的请求"""

    @authenticated
    @check_permission
    @gen.coroutine
    def get(self):
        """
        根据名字获取子账户列表
        """
        mch_id = self.current_user
        name = self.get_argument('q', None)
        all = self.get_argument('all', None)

        query = uline_session.query(MchSubUser.mch_sub_id.label('id'), MchSubUser.mch_sub_name). \
            filter(MchSubUser.mch_id == mch_id)

        if name:
            query = query.filter(MchSubUser.mch_sub_name.like(
                '{}%'.format(name)))

        if not all:
            query = query.filter(MchSubUser.status == 1)
        sub_users = query.limit(INDEX_PAGE_SIZE).all()

        data = [sub_user for sub_user in sub_users]
        response = common.scc_rsp(code=200, msg='success')
        response['data'] = data
        response['total_count'] = len(data)
        self.write(response)


class SubUserIndexHandler(MchAdminHandler):
    """处理子账户索引请求"""

    @authenticated
    def prepare(self):
        self.form = SubUserIndexForm(self)

    def get(self):
        if not self.form.validate() and self.form.status.data is not None:
            self.redirect('/dist/sub_user/')
            return

        page_index = int(self.get_argument("p", 1))
        sub_users, total_number = self.get_sub_users(page_index)
        navigate_html = self.get_navigate_html(total_number)
        self.render('merchant/system_settings/mchSubUserIndex.html',
                    navigate_html=navigate_html, data=sub_users, form=self.form,
                    total_num=total_number, QR_SCAN_URL=QR_SCAN_URL, mch_id=self.current_user)

    def get_sub_users(self, page_index):
        """根据条件获取对应子账户"""

        page_size = int(self.get_argument("page_size", INDEX_PAGE_SIZE))

        query = uline_session.query(MchSubUser).join(
            MchUserMchSubUser, MchUserMchSubUser.mch_sub_id == MchSubUser.mch_sub_id)

        query = query.filter(MchUserMchSubUser.mch_id == self.current_user)

        if self.form.create_at_start.data:
            query = query.filter(MchSubUser.create_at >=
                                 self.form.create_at_start.data)

        create_at_end = self.form.create_at_end.data
        if create_at_end:
            # 结束时间需要加一天，以包括结束当天的查询
            create_at_end += timedelta(days=1)
            query = query.filter(MchSubUser.create_at <= create_at_end)

        if self.form.status.data:
            query = query.filter(MchSubUser.status == self.form.status.data)

        # 支持匹配以输入开始的名字
        if self.form.mch_sub_name.data:
            query = query.filter(MchSubUser.mch_sub_name.like(
                '{}%'.format(self.form.mch_sub_name.data)))

        total_number = query.count()

        # 默认最新修改的排在前面
        query = query.order_by(MchSubUser.update_at.desc()). \
            limit(page_size).offset((page_index - 1) * page_size)

        sub_users = query.all()
        return sub_users, total_number


class SubUserAddHandler(MchAdminHandler):
    """处理子账户请求"""

    @authenticated
    def prepare(self):
        self.form = SubUserAddForm(self)
        self.form.mch_id = self.get_current_user()

    @gen.coroutine
    def post(self):
        """
        创建新的子账户
        """
        if not self.form.validate():
            response = common.f_rsp(code=500, msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            self.finish()
            return

        password = yield common.bcrypt_pwd(str(self.form.phone.data))
        new_sub_user = MchSubUser(
            # mch_id=self.current_user,
            mch_sub_name=self.form.mch_sub_name.data,
            login_name=self.form.login_name.data,
            email=self.form.email.data,
            phone=self.form.phone.data,
            password=password,
            status=self.form.status.data,
        )
        uline_session.add(new_sub_user)
        uline_session.commit()
        login_name_query = uline_session.query(MchSubUser.mch_sub_id).filter(
            MchSubUser.login_name == self.form.login_name.data).one()

        insert_new_employee = "insert into mch_user_mch_subuser (mch_id,mch_sub_id) values (%s,%s);"
        self.db.executeSQL(insert_new_employee,
                           (self.current_user, login_name_query[0]))

        response = common.scc_rsp(code=200)
        self.write(response)


class SubUserInfoHandler(MchAdminHandler):
    """查询子账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserInfoForm(self)
        self.form.mch_id = self.current_user

    @gen.coroutine
    def get(self):
        if not self.form.validate():
            response = common.f_rsp(msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            self.finish()
            return

        mch_sub_id = self.form.mch_sub_id.data
        sub_user = uline_session.query(MchSubUser).filter(
            MchSubUser.mch_sub_id == mch_sub_id).one()

        response = common.scc_rsp()
        response['data'] = sub_user.to_dict(excluded=('password', 'api_key'))
        self.write(response)


class SubUserEditHandler(MchAdminHandler):
    """查询子账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserEditForm(self)
        self.form.mch_id = self.current_user

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            response = common.f_rsp(msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            return self.finish()

        mch_sub_id = self.form.mch_sub_id.data
        sub_user = uline_session.query(MchSubUser).filter(
            MchSubUser.mch_sub_id == mch_sub_id)

        sub_user.update({
            'mch_sub_name': self.form.mch_sub_name.data,
            'email': self.form.email.data,
            'phone': self.form.phone.data,
            'status': self.form.status.data,
            'update_at': datetime.now(),
        })
        uline_session.commit()
        response = common.scc_rsp()
        self.write(response)


# 获取临时二维码
class WebChat(MchAdminHandler):

    def prepare(self):
        self.mch_sub_id = self.get_argument('mch_sub_id')
        self.form = GenerateQrcode(self)

    @gen.coroutine
    def get(self):

        if not self.form.validate():
            self.write(common.f_rsp(msg=(self.form.errors)['mch_sub_id']))
            return

        query = uline_session.query(MchSubUser.status).filter(
            MchSubUser.mch_sub_id == self.mch_sub_id).one()
        if query[0] != 1:
            rsp = common.f_rsp(code=406, msg='该员工处于禁用状态,暂不能绑定微信,请启用后再尝试')
        else:
            try:
                for i in range(3):
                    access_token = yield self.get_access_token(refresh=bool(i != 0))
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
        self.finish()
        return

    @gen.coroutine
    def get_ticket(self, access_token):

        body = {"expire_seconds": 604800, "action_name": "QR_SCENE",
                "action_info": {"scene": {"scene_id": self.mch_sub_id}}}
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


class GetOpenid(MchAdminHandler):

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
            parse_xml.get('EventKey'), \
            parse_xml.get('Event')

        if event == "unsubscribe":
            uline_session.query(MchSubUser.wx_open_id, MchSubUser.wx_id).filter(
                MchSubUser.wx_open_id == openid).update({"wx_open_id": None, "wx_id": None})
            uline_session.commit()
        elif event in ["SCAN", "subscribe"]:
            if not _scene_id:
                return
            scene_id = _scene_id[8:] if _scene_id.startswith(
                'qrscene_') else _scene_id
            if not scene_id.isdigit() and len(scene_id) != 8:
                return
            for i in range(3):
                access_token = yield self.get_access_token(refresh=bool(i != 0))
                result = yield self.get_employee_detail(access_token, openid, scene_id, event)
                if result == 2:
                    break
        return

    @gen.coroutine
    def get_employee_detail(self, access_token, openid, scene_id, event):

        url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN' \
            .format(access_token, openid)
        response = yield AsyncHTTPClient().fetch(url)
        data = json.loads(response.body)
        if data.get('errcode', 'error') != 'error':
            result = 1
        else:
            try:
                # scene_id = _scene_id[8:] if _scene_id.startswith(
                #     'qrscene_') else _scene_id
                uline_session.query(MchSubUser.wx_open_id, MchSubUser.wx_id).filter(
                    MchSubUser.mch_sub_id == scene_id).update(
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


class Getbindingstatus(MchAdminHandler):
    # 反馈绑定或者解绑状态

    def prepare(self):
        self.mch_sub_id = self.get_argument('mch_sub_id')
        self.binding_status = self.get_argument("binding")  # 1为绑定,2为解绑

    def get(self):
        try:
            msg = {"code": 200, "msg": 'success'}
            if self.binding_status == u'1':
                query = uline_session.query(MchSubUser.wx_open_id, MchSubUser.wx_id).filter(
                    MchSubUser.mch_sub_id == self.mch_sub_id).one()
                if all(query):
                    msg = {"code": 200, "msg": 1}  # 1 为绑定成功,2 为解绑成功
            elif self.binding_status == u'2':
                uline_session.query(MchSubUser.wx_open_id, MchSubUser.wx_id).filter(
                    MchSubUser.mch_sub_id == self.mch_sub_id).update({"wx_open_id": None, "wx_id": None})
                uline_session.commit()
                msg = {"code": 200, "msg": 2}
        except Exception as err:
            log.exception.exception(err)
            msg = {"code": 406, "msg": "操作失败,请重新尝试!"}
        self.write(msg)
        self.finish()
        return
