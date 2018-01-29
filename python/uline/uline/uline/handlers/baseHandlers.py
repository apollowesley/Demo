# -*- coding:utf-8 -*-
import functools
import hashlib
import random
from uline.public.common import bcrypt_pwd, bcrypt_pwd_new
import datetime
import tornado.web
import traceback
from tornado import gen, stack_context
from tornado.escape import utf8
from tornado.httpclient import AsyncHTTPClient
from tornado.util import unicode_type
from raven.contrib.tornado import SentryMixin
from tornado.web import HTTPError
from concurrent.futures import ThreadPoolExecutor

from uline.model.uline.base import uline_session
from uline.model.uline_trade.base import trade_session
from uline.utils.tor import ThreadRequestContext
from uline.model.uline.user import Employee, BkUser, UbUser, DtUser, UnionEmployee
from uline.model.uline.info import UserProfile
from uline.public.baseDB import DbClient
from uline.public.baseTradeDB import TradeDbClient
from uline.public import log
from uline.utils import session
from uline.utils.wxpay.merchantInletToWxV2 import UpdateMerchantInletToWx, GetMetchantInfoFromWx
from uline.utils.wxpay.util import xml_to_dict
from uline.settings import BANK_NAME
from uline.public.log import detail
from uline.utils.json_utils import LazableJSONEncoder
import json
import time
from uline.settings import app_id, app_secret, env, MESSAGE_URL
import urllib

from uline.public.constants import FEATURE_SWITCH


# Handlers 共享的 Handler 方法。API 使用不正确错误处理

class UlineSentryMixin(SentryMixin):

    def _capture(self, call_name, data=None, **kwargs):
        if env.upper() in ["LOCAL", "DEV"]:
            return
        return super(UlineSentryMixin, self)._capture(call_name, data, **kwargs)


class BaseHandler(UlineSentryMixin, tornado.web.RequestHandler):

    executor = ThreadPoolExecutor(20)

    def __init__(self, *args, **kwargs):
        self.dynamic_value = {}
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.session = session.Session(self.application.session_manager, self)

    def on_finish(self):
        uline_session.remove()
        trade_session.remove()
        self.udbsession.close()

    def _execute(self, transforms, *args, **kwargs):
        global_data = {"request_id": id(self)}
        with stack_context.StackContext(
                functools.partial(ThreadRequestContext, **global_data)):
            self.udbsession = uline_session()
            return super(
                BaseHandler, self)._execute(transforms, *args, **kwargs)

    def head(self, *args, **kwargs):
        self.write('')

    def initialize(self):
        self.add_header("Access-Control-Allow-Origin", "*")

    def write(self, chunk):
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if not isinstance(chunk, (bytes, unicode_type, dict)):
            message = "write() only accepts bytes, unicode, and dict objects"
            if isinstance(chunk, list):
                message += ". Lists not accepted for security reasons; see http://www.tornadoweb.org/en/stable/web.html#tornado.web.RequestHandler.write"
            raise TypeError(message)
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk, cls=LazableJSONEncoder)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            try:
                log.request.info(">>>>>>>>>> " + str(chunk))
            except Exception as err:
                log.request.info(">>>>>>>>>> " + str(err))
        chunk = utf8(chunk)
        self._write_buffer.append(chunk)

    def write_error(self, status_code, **kwargs):
        if int(status_code) in (403, 405):
            return
        if "exc_info" in kwargs:
            for line in traceback.format_exception(*kwargs["exc_info"]):
                log.exception.info(line)
        if status_code == 500:
            self.render('common/error_500.html')
        elif status_code == 404:
            self.render('common/error_404.html')
        else:
            self.write(str(status_code))
            self.finish()

    def get_client_ip(self):
        try:
            real_ip = self.request.META['HTTP_X_FORWARDED_FOR']
            regip = real_ip.split(",")[0]
        except Exception:
            try:
                regip = self.request.META['REMOTE_ADDR']
            except Exception:
                regip = ""
        return regip

    def get_navigate_html(self, counts=0, pagesize=10, **query_args):
        # 分页处理
        pageindex = int(self.get_argument("p", 1))
        page_number = 0
        if counts > 0:
            if counts % pagesize == 0:
                page_number = counts / pagesize
            else:
                page_number = counts / pagesize + 1
        is_pre = False
        is_next = False
        if page_number > 1 and pageindex > 1:
            is_pre = True
        if page_number > 1 and pageindex < page_number:
            is_next = True
        query_info = ''
        if query_args:
            query_info = '&{}'.format(urllib.urlencode(query_args))
        return self.render_string("common/navigate.html", pageindex=pageindex, page_number=page_number, is_pre=is_pre,
                                  is_next=is_next, counts=counts, query_info=query_info)

    def get_template_namespace(self):
        """
        添加env（表名当前属于那个环境）到模板
        """
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update({
            'env': env,
        })
        return ns

    def render(self, template_name, **kwargs):
        """
        Arguments:
            template_name {str} -- 模板路径
            **kwargs {dict} -- 填写那些可能变化的参数值
        """
        unchanged_params = self.generate_unchanged_render_params()
        unchanged_params['INTER_BANK'] = FEATURE_SWITCH.get("INTER_BANK")
        if isinstance(unchanged_params, dict):
            self.dynamic_value.update(unchanged_params)
        self.dynamic_value.update(kwargs)
        super(BaseHandler, self).render(template_name, **self.dynamic_value)

    def generate_unchanged_render_params(self):
        """生成不变的参数，默认为空

            return：字典，如果不需要，返回空字典即可
        """
        return {}

    def map_current_user(self):
        return {
            "ub": ["ub_id", "ub_name"],
            "bk": ["bk_id", "bk_name"],
            "dt": ["dt_id", "dt_name"],
            "mch": ["mch_id", "mch_name"],
            "mr": ["chain_id", "chain_name"],
            "ibk": ["inter_bk_id", "inter_bk_name"]
        }

    def get_login_url(self):
        return '/account/'


# 图片 - 静态文件读取加查找文件路径错误处理
class ImageHandler(tornado.web.StaticFileHandler):
    """docstring for ImageHandler"""

    def write_error(self, status_code, **kwargs):
        if status_code == 500:
            self.render('common/error_500.html')
        elif status_code == 404:
            self.render('common/error_404.html')
        else:
            self.write(str(status_code))
            self.finish()


# 文件 - 静态文件读取加查找文件路径错误处理
class StaticHandler(tornado.web.StaticFileHandler):

    def get(self, path, include_body=True):
        self.set_header("Access-Control-Allow-Origin", "*")
        super(StaticHandler, self).get(path, include_body)

    def write_error(self, status_code, **kwargs):
        self.finish({str(status_code): "a nicer message!"})


# 错误 API 链接处理
class ErrorLinkHandler(BaseHandler):
    """docstring for ErrorLinkHandler"""

    def get(self):
        self.render('common/error_404.html')


class DtAdminHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('dt_id')

    def get_current_subuser(self):
        return self.session.get('dt_sub_id')

    def get_dt_user_name(self, dt_id):
        return self.db.selectSQL("select dt_name from dt_user where dt_id=%s", (dt_id,))

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
        self.uline_session = uline_session
        params = {
            'has_jdpay': FEATURE_SWITCH.get('JD_PAY', False),
            'can_use_unionpay': FEATURE_SWITCH.get('UNION_PAY', False),

        }
        self.dynamic_value.update(params)

    def get_bank_for_dt(self, dt_id):
        selSql = """SELECT bk.bk_id, bk.bk_name, bk.bk_id FROM dt_inlet_info  dt
                INNER JOIN bk_user  bk on  bk.bk_id=dt.bk_id WHERE dt.dt_id = %s"""
        db_ret = self.db.selectSQL(selSql, (dt_id,))
        return db_ret


class ChainAdminHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('chain_id')

    def get_current_subuser(self):
        return self.session.get('chain_sub_id')

    def get_dt_user_name(self, chain_id):
        return self.db.selectSQL("select dt_name from dt_user where dt_id=%s and parent_id is not null", (chain_id,))

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
        params = {
            'has_jdpay': FEATURE_SWITCH.get('JD_PAY', False),

        }
        self.dynamic_value.update(params)

    def get_bank_for_chain(self, chain_id):
        selSql = """SELECT bk.bk_id, bk.bk_name, bk.bk_id FROM dt_inlet_info  dt
                INNER JOIN bk_user  bk on  bk.bk_id=dt.bk_id WHERE dt.dt_id = (
                SELECT parent_id FROM dt_inlet_info WHERE dt_id = %s)"""
        db_ret = self.db.selectSQL(selSql, (chain_id,))
        return db_ret

    @gen.coroutine
    def get_access_token(self, refresh=False):
        access_token = self.rdb.get('access_token')
        if not refresh and access_token:
            raise gen.Return(access_token)
        res = yield AsyncHTTPClient().fetch(
            u"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
            .format(app_id, app_secret))
        res = json.loads(res.body)
        access_token = res['access_token']
        self.rdb.set('access_token', access_token, 7200)
        raise gen.Return(access_token)


class IntBkAdminHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('inter_bk_id')

    def get_current_subuser(self):
        return self.session.get('bk_sub_id')

    def get_ub_user_name(self, bk_id):
        return self.db.selectSQL("select bk_name from bk_user where bk_id=%s", (bk_id,))

    def get_bk_name(self):
        return self.session.get('inter_bk_name') or self.get_secure_cookie('inter_bk_name')

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
        self.uline_session = uline_session
        params = {
            'has_jdpay': FEATURE_SWITCH.get('JD_PAY', False),

        }
        self.dynamic_value.update(params)

    @gen.coroutine
    def update_mch_info2wx(self, update_info, APPID, WX_MCH_ID, WXPAY_KEY,
                           WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
        """修改微信端app支付渠道商信息.

            Args:
                update_info (type:dict): 需要更新的信息，相应信息为
                                    service_phone: 客服号码
                                    wx_mch_id: app商户微信端ID。

            Returns:
                dict ，包含反馈的信息
        """

        mchInletToWx = UpdateMerchantInletToWx(APPID, WX_MCH_ID, WXPAY_KEY)
        data = mchInletToWx.handle()(
            merchant_shortname=update_info['short_name'],
            service_phone=update_info['service_phone'],
            sub_mch_id=update_info['wx_mch_id'],
        )
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(
            "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=modify",
            method='POST', body=data,
            client_key=WX_PRIVATE_KEY,
            client_cert=WX_PUB_KEY,
            ca_certs=WX_ROOT_CA
        )
        ret = xml_to_dict(response.body).get('root')
        log.detail.info(response.body)
        if not ret:
            ret = dict(result_code='FAIL')
        raise gen.Return(ret)

    @gen.coroutine
    def get_mch_info_from_wx(self, search_info, APPID, WX_MCH_ID, WXPAY_KEY,
                             WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
        getMchInfoFromWx = GetMetchantInfoFromWx(APPID, WX_MCH_ID, WXPAY_KEY)
        data = getMchInfoFromWx.handle()(**search_info)
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(
            "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=query",
            method='POST', body=data,
            client_key=WX_PRIVATE_KEY,
            client_cert=WX_PUB_KEY,
            ca_certs=WX_ROOT_CA
        )
        ret = xml_to_dict(response.body).get('root')
        detail.info('get_mch_info_from_wx:{}'.format(ret))
        mch_info_in_wx = None
        if ret:
            mchinfos = ret.get('mchinfo', [])
            if isinstance(mchinfos, dict):
                mchinfos = [mchinfos]
            for each_mch in mchinfos:
                if each_mch:
                    mch_id = each_mch.get('mch_id', '')
                    if mch_id and mch_id == search_info.get('sub_mch_id'):
                        mch_info_in_wx = each_mch
                        break
        if not mch_info_in_wx:
            log.exception.info(
                'no merchant info in wx.\n Data: {}'.format(json.dumps(search_info, indent=4, ensure_ascii=False)))
        raise gen.Return(mch_info_in_wx)


class BkAdminHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('bk_id') or self.get_secure_cookie('bk_id')

    def get_current_subuser(self):
        return self.session.get('bk_sub_id')

    def get_ub_user_name(self, bk_id):
        return self.db.selectSQL("select bk_name from bk_user where bk_id=%s", (bk_id,))

    def get_bk_name(self):
        return self.session.get('bk_name') or self.get_secure_cookie('bk_name')

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
        self.uline_session = uline_session
        params = {
            'OPEN_DISCOUNT': FEATURE_SWITCH.get('OPEN_DISCOUNT', False),
            'OPEN_D0': FEATURE_SWITCH.get('OPEN_D0', False),
            'has_jdpay': FEATURE_SWITCH.get('JD_PAY', False),

        }
        self.dynamic_value.update(params)

    @gen.coroutine
    def update_mch_info2wx(self, update_info, APPID, WX_MCH_ID, WXPAY_KEY,
                           WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
        """修改微信端app支付渠道商信息.

            Args:
                update_info (type:dict): 需要更新的信息，相应信息为
                                    service_phone: 客服号码
                                    wx_mch_id: app商户微信端ID。

            Returns:
                dict ，包含反馈的信息
        """

        mchInletToWx = UpdateMerchantInletToWx(APPID, WX_MCH_ID, WXPAY_KEY)
        data = mchInletToWx.handle()(
            merchant_shortname=update_info['short_name'],
            service_phone=update_info['service_phone'],
            sub_mch_id=update_info['wx_mch_id'],
        )
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(
            "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=modify",
            method='POST', body=data,
            client_key=WX_PRIVATE_KEY,
            client_cert=WX_PUB_KEY,
            ca_certs=WX_ROOT_CA
        )
        ret = xml_to_dict(response.body).get('root')
        log.detail.info(response.body)
        if not ret:
            ret = dict(result_code='FAIL')
        raise gen.Return(ret)

    @gen.coroutine
    def get_mch_info_from_wx(self, search_info, APPID, WX_MCH_ID, WXPAY_KEY,
                             WX_PRIVATE_KEY, WX_PUB_KEY, WX_ROOT_CA):
        getMchInfoFromWx = GetMetchantInfoFromWx(APPID, WX_MCH_ID, WXPAY_KEY)
        data = getMchInfoFromWx.handle()(**search_info)
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(
            "https://api.mch.weixin.qq.com/secapi/mch/submchmanage?action=query",
            method='POST', body=data,
            client_key=WX_PRIVATE_KEY,
            client_cert=WX_PUB_KEY,
            ca_certs=WX_ROOT_CA
        )
        ret = xml_to_dict(response.body).get('root')
        detail.info('get_mch_info_from_wx:{}'.format(ret))
        mch_info_in_wx = None
        if ret:
            mchinfos = ret.get('mchinfo', [])
            if isinstance(mchinfos, dict):
                mchinfos = [mchinfos]
            for each_mch in mchinfos:
                if each_mch:
                    mch_id = each_mch.get('mch_id', '')
                    if mch_id and mch_id == search_info.get('sub_mch_id'):
                        mch_info_in_wx = each_mch
                        break
        if not mch_info_in_wx:
            log.exception.info(
                'no merchant info in wx.\n Data: {}'.format(json.dumps(search_info, indent=4, ensure_ascii=False)))
        raise gen.Return(mch_info_in_wx)


class OfclAdminHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('ub_id')

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client

        params = {
            'OPEN_DISCOUNT': FEATURE_SWITCH.get('OPEN_DISCOUNT', False),
            'OPEN_D0': FEATURE_SWITCH.get('OPEN_D0', False),
            'has_jdpay': FEATURE_SWITCH.get('JD_PAY', False),
            'can_use_unionpay': FEATURE_SWITCH.get('UNION_PAY', False),
        }
        self.dynamic_value.update(params)


class MchAdminHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('mch_id')

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
        params = {
            'has_jdpay': FEATURE_SWITCH.get('JD_PAY', False),
        }
        self.dynamic_value.update(params)

    @gen.coroutine
    def get_access_token(self, refresh=False):
        access_token = self.rdb.get('access_token')
        if not refresh and access_token:
            raise gen.Return(access_token)
        res = yield AsyncHTTPClient().fetch(
            u"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
            .format(app_id, app_secret))
        res = json.loads(res.body)
        access_token = res['access_token']
        self.rdb.set('access_token', access_token, 7200)
        raise gen.Return(access_token)


class CommanHandler(BaseHandler):

    def get_current_user(self):
        return self.session.get('mch_id') or self.session.get('ub_id') or self.session.get(
            'bk_sub_id') or self.session.get('bk_id') or self.session.get('dt_id') or self.session.get(
            'dt_sub_id') or self.session.get('chain_id') or self.session.get('inter_bk_id')

    def get_user(self):
        return {"2": self.session.get('dt_id'),
                "3": self.session.get('chain_id'),
                "4": self.session.get('mch_id'),
                "1": self.session.get('bk_id'),
                "5": self.session.get('ub_id')
                }

    def initialize(self):
        self.db = DbClient()
        self.tdb = TradeDbClient()
        self.rdb = self.application.client
        params = {'OPEN_DISCOUNT': FEATURE_SWITCH.get('OPEN_DISCOUNT', False),
                  'OPEN_D0': FEATURE_SWITCH.get('OPEN_D0', False), }
        self.dynamic_value.update(params)

    def get_bk_name(self):
        return self.session.get('bk_name') or self.get_secure_cookie('bk_name') or self.session.get('inter_bk_name')

    @gen.coroutine
    def send_auth_code(self, auth_code, key, reciver, send_type):

        http_client = AsyncHTTPClient()
        data = {'env': env, 'reciver': reciver, 'body': u'您的验证码是{},一个小时后失效。'.format(auth_code)}
        url = MESSAGE_URL + '/v1/{}'.format(send_type)
        response = yield http_client.fetch(url, method='POST', body=json.dumps(data))
        # 测试```````````````````````
        # self.rdb.set(key, auth_code, 60 * 60)
        # 测试```````````````````````
        if str(response.body) == '2' and self.rdb.set(key, auth_code, 60 * 60):
            msg = {'code': 200, 'msg': 'success', 'data': reciver}
        else:
            msg = {'code': 406, 'msg': 'fail'}
            # msg = {'code': 200, 'msg': 'success', 'data': reciver}

        raise gen.Return(msg)

    def update_password(self, new_pwd, update_id):
        key = str(update_id) + ':AuthForgetPass'
        password = bcrypt_pwd_new(str(new_pwd))
        update_at = datetime.datetime.now()
        uline_session.query(Employee).filter(Employee.id == update_id).update(
            {"login_passwd": password, "update_at": update_at})
        uline_session.commit()
        self.rdb.delete(key)
        return

    def get_user_profile(self, query_id):
        user_profile = uline_session.query(UserProfile).join(
            Employee, Employee.user_id == UserProfile.id).filter(Employee.id == query_id).first()
        return user_profile

    def get_token(self, query_id, expiration):
        token = hashlib.sha1(str(query_id) + str(time.time()) + str(random.randint(10000, 999999))).hexdigest()
        self.rdb.set(str(token), query_id, expiration)
        return token

    def get_auth_code(self, login_id):
        key = str(login_id) + ':AuthForgetPass'
        if self.rdb.get(key):
            auth_code = self.rdb.get(key)
        else:
            auth_code = str(random.randint(10000, 999999))
        return [auth_code, key]

    def check_auth_code(self, auth_code, employee_id):
        key = str(employee_id) + ':AuthForgetPass'
        d = self.rdb.get(key)
        if self.rdb.get(key) == auth_code:
            return True
        return False

    def get_sys_type_code(self, sys_id, sys_type_code):
        if sys_type_code == "bk":
            bk_type = uline_session.query(BkUser.bk_type).filter(BkUser.bk_id == sys_id).one()[0]
            sys_type_code = "ibk" if bk_type in [2, "2"] else sys_type_code
        return sys_type_code

    def get_user_id(self, sys_type_code):
        return {"dt": self.session.get('dt_id'),
                "mr": self.session.get('chain_id'),
                "mch": self.session.get('mch_id'),
                "bk": self.session.get('bk_id'),
                "ub": self.session.get('ub_id'),
                "ibk": self.session.get('inter_bk_id')
                }[sys_type_code]
