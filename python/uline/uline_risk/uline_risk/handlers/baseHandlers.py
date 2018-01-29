# -*- coding:utf-8 -*-
import functools
import json
from datetime import datetime
import traceback
import decimal

import six
from tornado import stack_context
from tornado.web import RequestHandler, HTTPError
from tornado.web import utf8

from raven.contrib.tornado import SentryMixin

from uline_risk.model.uline.base import uline_session
from uline_risk.model.uline_trade.base import trade_session
from uline_risk.utils.log import exception as error_log
from uline_risk.utils.tor import ThreadRequestContext
from uline_risk.utils.json_utils import LazableJSONEncoder
from uline_risk.public.code_msg import RETURN_MSG


def tojson(data, ensure_ascii=True, default=False, **kwargs):
    def serializable(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        raise TypeError

    _default = serializable if default else None
    return json.dumps(data,
                      ensure_ascii=ensure_ascii,
                      default=_default,
                      separators=(',', ':'),
                      **kwargs).replace("</", "<\\/")


class RESTfulHandler(SentryMixin, RequestHandler):

    def get_current_time(self):
        return datetime.now()

    def valid_params(self):
        if hasattr(self, 'form') and not self.form.validate():
            raise RESTfulException(error_type='params_error', error_detail=self.form.errors)

    def load_json_body_data(self):
        return json.loads(self.request.body)

    def data_received(self, chunk):
        pass

    def check_xsrf_cookie(self):
        """ RESTful 禁用 XSRF 保护机制 """
        pass

    def on_finish(self):
        uline_session.remove()
        trade_session.remove()

    def _execute(self, transforms, *args, **kwargs):
        global_data = {"request_id": id(self)}
        with stack_context.StackContext(
                functools.partial(ThreadRequestContext, **global_data)):
            return super(
                RESTfulHandler, self)._execute(transforms, *args, **kwargs)

    def write_error(self, status_code, **kwargs):
        """覆盖自定义错误."""
        # debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]
            if isinstance(e, RESTfulException):
                pass
            elif isinstance(e, HTTPError):
                e = RESTfulException(e.status_code)
            else:
                e = RESTfulException(500)
            exception = "".join([ln for ln in traceback.format_exception(*exc_info)])
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

    def generate_response_msg(self, return_type='success', **kwargs):
        msg = {}
        msg.update(RETURN_MSG.get(return_type, {}))
        msg.update(kwargs)
        return msg

    def write(self, chunk):
        """Writes the given chunk to the output buffer.

        To write the output to the network, use the flush() method below.

        If the given chunk is a dictionary, we write it as JSON and set
        the Content-Type of the response to be ``application/json``.
        (if you want to send JSON as a different ``Content-Type``, call
        set_header *after* calling write()).

        Note that lists are not converted to JSON because of a potential
        cross-site security vulnerability.  All JSON output should be
        wrapped in a dictionary.  More details at
        http://haacked.com/archive/2009/06/25/json-hijacking.aspx/ and
        https://github.com/facebook/tornado/issues/1009
        """
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if not isinstance(chunk, (bytes, str, dict)):
            message = "write() only accepts bytes, unicode, and dict objects"
            if isinstance(chunk, list):
                message += ". Lists not accepted for security reasons;"
                message += " see http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write"
            raise TypeError(message)
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk, cls=LazableJSONEncoder).replace("</", "<\\/")
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)


class RESTfulException(Exception):
    """ API 错误异常模块：
        API服务器产生内部服务器错误时总是向客户返回JSON格式的数据.
    """
    _error_types = {
        400: "参数错误",
        401: "认证失败",
        403: "未经授权",
        404: "终端错误",
        405: "未许可的方法",
        500: "服务器错误"
    }

    def __init__(self, error_type="", error_detail=None):
        self.error_msg = {}
        if isinstance(error_type, int):
            msg = {
                    "code": error_type,
                    'msg': "FAIL",
                    "error_msg": RESTfulException._error_types.get(error_type, "未知错误")
            }
            self.error_msg.update(msg)
        elif isinstance(error_type, str):
            self.error_msg.update(RETURN_MSG.get(error_type, {}))
        if error_detail:
            self.error_msg['error_details'] = error_detail

    def __str__(self):
        return tojson(self.error_msg, default=True, ensure_ascii=False)

    def _set_message(self, err, names):
        for name in names:
            v = getattr(self, name)
            if v:
                err[name] = v


class DefaultRESTfulHandler(RESTfulHandler):
    """ 不存在的RESTfultHandler请求都返回JSON格式404错误
        *** 在相应的urls最末行设置如(r".*", DefaultRESTfulHandler)路由即可
    """

    def prepare(self):
        super(DefaultRESTfulHandler, self).prepare()
        raise RESTfulException(404)
