# -*- coding: utf-8 -*-

from uline.model.uline.other import GatherMchsEmailInfo
from uline.model.uline.base import uline_session
from uline.handlers.baseHandlers import DtAdminHandler
from tornado.web import authenticated
from .form import ResendEmailForm
from tornado.gen import coroutine, Return
from uline.settings import env
from tornado.httpclient import AsyncHTTPClient
import json
from datetime import timedelta
from uline.model.uline.info import DtInletInfo
from uline.public import log
from uline.public.permit import check_permission

from sqlalchemy import func, desc, cast, DateTime

INDEX_PAGE_SIZE = 10
HOST_IP = '127.0.0.1'

DT_SEND = """尊敬的{dt_name}：
以下是您在{auth_date}通过ULINE审核的商户汇总,请点击链接进行下载:
{download_url}

重要信息,请注意保密

广州优畅信息技术有限公司
客服电话：400-8047555
"""


class ShowGatherEmailSend(DtAdminHandler):

    @authenticated
    @check_permission
    def get(self):
        p = int(self.get_argument("p", 1))
        dt_id = self.current_user
        emails = uline_session.query(GatherMchsEmailInfo).filter(GatherMchsEmailInfo.dt_id == dt_id)
        emails = emails.order_by(GatherMchsEmailInfo.create_at.desc())
        total_num = emails.count()
        emails = emails.order_by(GatherMchsEmailInfo.create_at.desc()).limit(10).offset((p - 1) * 10)
        emails = emails.all()
        send_email = []
        if emails:
            for email in emails:
                email_title = (email.create_at - timedelta(1)).strftime("%Y-%m-%d") + "商户开户汇总"
                send_email.append({"email_title": email_title,
                                   "create_at": email.create_at.strftime('%Y-%m-%d %H:%M:%S')})
        navigate_html = self.get_navigate_html(total_num)
        self.render("distributor/system_settings/gather_email.html", emails=send_email, navigate_html=navigate_html)
        return


class ResendEmail(DtAdminHandler):

    @authenticated
    @coroutine
    def post(self):
        form = ResendEmailForm(self)
        if not form.validate():
            self.write({"code": 406, "msg": "需要下载日期参数"})
            return
        resend_date = form.resend_date.data[:10]

        email = uline_session.query(GatherMchsEmailInfo).\
            filter(GatherMchsEmailInfo.dt_id == self.current_user,
                   cast(func.to_char(GatherMchsEmailInfo.create_at, 'YYYY-MM-DD'), DateTime) == resend_date)
        email_select = email.first()
        msg = "发送失败,请联系客服"
        try:
            response = yield self.send_active_dt_email(email_select)
            msg = "发送成功" if response and response.body == "2" else "发送失败,请联系客服"
            email.update({'status': 2})
            uline_session.commit()
        except Exception as err:
            log.exception.info(err)
        self.write({"code": 406, "msg": msg})
        return

    @coroutine
    def send_active_dt_email(self, email_info):
        send_date = (email_info.create_at - timedelta(1)).strftime("%Y-%m-%d").split("-")
        send_date = "{}年{}月{}日".format(*send_date)

        dt_ = uline_session.query(DtInletInfo).filter(DtInletInfo.dt_id == self.current_user).one()

        dt_info = {"dt_name": dt_.dt_name, "auth_date": send_date, "download_url": email_info.download_url}
        download_url_ = {'SPD_PROD': u'http://cms.spd.uline.cc', 'CMBC_PROD': u'http://cms.cmbxm.mbcloud.com',
                         'LOCAL': u'http://127.0.0.1:8893', "DEV": u'http://mch.stage.uline.cc',
                         'SPDLOCAL': u'http://127.0.0.1:8893'}

        dt_info["download_url"] = "".join([download_url_[env], '/static/downloads/',
                                           str(dt_.dt_id), "/", dt_info["download_url"]])
        data = {'env': env, 'reciver': email_info.email, 'title': u'uline商户汇总激活信息',
                'body': DT_SEND.format(**dt_info)}
        http_client = AsyncHTTPClient()
        MESSAGE_URL = 'http://{}:6789'.format(HOST_IP)
        url = MESSAGE_URL + '/v1/email'
        response = yield http_client.fetch(url, body=json.dumps(data), method='POST')
        raise Return(response)
