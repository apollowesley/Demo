# -*- coding:utf-8 -*-
import functools

import six
import tornado.web
import traceback
from base64 import b64decode
from datetime import datetime, timedelta
from hashlib import md5
from tornado.web import HTTPError
from uline_api.util import session
from uline_api.util.log import (
    error_log,
    # access_log
)
from uline_api.util.common import tojson
from uline_api.model.uline.user import DtUser
from tornado import stack_context
from uline_api.util.tor import ThreadRequestContext
from uline_api.model.uline.base import uline_session
from uline_api.model.uline_trade.base import trade_session
from wtforms.fields.core import UnboundField


# 参照 https://github.com/Coldwings/Campanella-rapidfork/blob/master/rapidfork/views/base.py

class RESTfulHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        super(RESTfulHandler, self).__init__(*args, **kwargs)
        self.session = session.Session(self.application.session_manager, self)

    def __getattribute__(self, item):
        ret = object.__getattribute__(self, item)
        if isinstance(ret, UnboundField):
            form = object.__getattribute__(self, 'form')
            return getattr(form, item).data
        return ret

    # 作验证使用
    def prepare(self):
        # TODO mch dt p 都需要提供接口认证
        authorization = self.request.headers.get('Authorization')
        if authorization is None:
            raise RESTfulHTTPError(
                401, content={'Authorization': ['Header中没有Authorization字段']})

        if authorization.startswith('Basic '):
            return self.base64_validate()

        elif authorization.startswith('Uline '):
            return self.hmac_validate()
        else:
            raise RESTfulHTTPError(401, content={'Authorization': [
                'Header中Authorization字段格式错误']})

    def base64_validate(self):
        authorization = self.request.headers.get('Authorization')
        sign = authorization.split('Basic ')[-1]
        try:
            sign = b64decode(sign)
        except:
            raise RESTfulHTTPAuthError(content=u'Authorization认证失败，非有效的base64字符串')
        try:
            dt_id, api_key = sign.split(':', 1)
        except ValueError:
            raise RESTfulHTTPAuthError(content=u'Header中Authorization字段格式错误，必须为"渠道商号:渠道商密钥"格式')

        if not dt_id:
            raise RESTfulHTTPAuthError(content=u'Authorization认证失败，渠道商号不能为空')

        if not dt_id.isdigit():
            raise RESTfulHTTPAuthError(content=u'Authorization认证失败，渠道号非法，必须只包含数字')

        if api_key.strip() == "":
            raise RESTfulHTTPAuthError(content=u'Authorization认证失败，渠道商密钥不能为空')

        dt_user = DtUser.get_by(dt_id=dt_id).first()
        if not dt_user:
            raise RESTfulHTTPAuthError(content=u'Authorization认证失败，渠道商不存在')

        elif dt_user.api_key != api_key:
            raise RESTfulHTTPAuthError(content=u'Authorization认证失败，渠道商密钥错误')
        else:
            self.dt_id = dt_id

    def hmac_validate(self):
        authorization = self.request.headers.get('Authorization')
        sign = authorization.split('Uline ')[-1]
        try:
            dt_id, sign = sign.split(':', 1)
        except ValueError:
            raise RESTfulHTTPAuthError(
                content=u'Header中Authorization字段格式错误，必须为："Authorization: Uline <id>:<signature>"')
        date = self.request.headers.get('Date')
        if date is None:
            raise RESTfulHTTPAuthError(content='HTTP请求头中没有Date字段')
        try:
            strf_date = datetime.strptime(
                date, '%a, %d %b %Y %H:%M:%S GMT')
        except:
            raise RESTfulHTTPAuthError(
                content=u'HTTP请求头中Date字段不合法, 必须为类似这样的格式:"Wed, 05 Jul 2017 10:27:19 GMT"')
        if datetime.utcnow() - strf_date > timedelta(minutes=1):
            raise RESTfulHTTPAuthError(content=u'HTTP请求头中Date距离现在已经超过一分钟')

        method = self.request.method
        path = self.request.path
        length = self.request.headers.get('Content-Length', '0')

        pre_sign_body = '&'.join([method, path, date, length])
        dt_user = DtUser.get_by(dt_id=dt_id).first()
        if not dt_user:
            raise RESTfulHTTPAuthError(content=u"Authorization认证失败,提供的渠道号不存在")

        if not dt_user.api_key:
            raise RESTfulHTTPAuthError(
                        content="Authorization认证失败,提供的渠道号没有开通api权限，请联系客服处理")

        api_key = dt_user.api_key
        sign_body = '&'.join([method, path, date, length, api_key])
        if md5(sign_body).hexdigest() != sign:
            raise RESTfulHTTPAuthError(
                content='Authorization认证失败, 签名不匹配， 服务器端进行签名的字符串为：{}。'.format(pre_sign_body))
        else:
            self.dt_id = dt_id

    def on_finish(self):
        uline_session.remove()
        trade_session.remove()

    def _execute(self, transforms, *args, **kwargs):
        global_data = {"request_id": id(self)}
        with stack_context.StackContext(
                functools.partial(ThreadRequestContext, **global_data)):
            return super(
                RESTfulHandler, self)._execute(transforms, *args, **kwargs)

    def finish(self, chunk=None, message=None):
        if chunk is None:
            chunk = {}
        if isinstance(chunk, dict):
            chunk = {"code": self._status_code, "content": chunk}
            if message:
                chunk["message"] = message
            chunk = tojson(chunk, default=True)
        else:
            chunk = six.text_type(chunk)

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        super(RESTfulHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        """覆盖自定义错误."""
        # debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]
            if isinstance(e, RESTfulHTTPError):
                pass
            elif isinstance(e, HTTPError):
                e = RESTfulHTTPError(e.status_code)
            else:
                e = RESTfulHTTPError(500)
            exception = "".join([ln for ln in traceback.format_exception(
                *exc_info)])
            if status_code == 500:
                error_log.error(exception)

            self.clear()
            self.set_status(200)  # 使 RESTful 接口错误总是返回成功(200 OK)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.finish(six.text_type(e))
        except Exception:
            error_log.error(traceback.format_exc())
            return super(RESTfulHandler, self).write_error(
                status_code, **kwargs)


class RESTfulHTTPError(HTTPError):
    """ API 错误异常模块：
        API服务器产生内部服务器错误时总是向客户返回JSON格式的数据.
    """
    _error_types = {
        400: u"参数错误",
        401: u"认证失败",
        403: u"未经授权",
        404: u"URL不存在",
        405: u"未许可的方法",
        500: u"服务器错误"
    }

    def __init__(
            self, status_code=400, error_detail="",
            error_type="", content="", log_message=None, *args):
        super(RESTfulHTTPError, self).__init__(
            int(status_code), log_message, *args)
        self.error_detail = error_detail
        self.error = {'type': error_type} if error_type else {
            'type': self._error_types.get(self.status_code, u"未知错误")
        }
        self.content = content if content else {}

    def __str__(self):
        message = {"code": self.status_code}
        self._set_message(message, ["error", "content"])
        if self.error_detail:
            message["error"]["detail"] = self.error_detail
        return tojson(message, default=True)

    def _set_message(self, err, names):
        for name in names:
            v = getattr(self, name)
            if v:
                err[name] = v

class RESTfulHTTPAuthError(RESTfulHTTPError):
    def __init__(
            self, status_code=401, error_detail="",
            error_type="", content="", log_message=None, *args):
        content = {'Authorization': [content]}
        super(RESTfulHTTPAuthError, self).__init__(
            int(status_code), error_detail, error_type, content, log_message, *args)

class DefaultRESTfulHandler(RESTfulHandler):
    """ 不存在的RESTfultHandler请求都返回JSON格式404错误
        *** 在相应的urls最末行设置如(r".*", DefaultRESTfulHandler)路由即可
    """

    def prepare(self):
        raise RESTfulHTTPError(404)
