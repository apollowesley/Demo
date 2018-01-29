# -*- coding: utf-8 -*-
import hashlib
import json
from uline.settings import auth_access_token
import xmltodict
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.web import authenticated, HTTPError, asynchronous
from uline.public import common, log
from collections import defaultdict
from uline.handlers.baseHandlers import ChainAdminHandler
from uline.settings import QR_SCAN_URL
from .sub_user_form import SubUserIndexForm, SubUserAddForm, SubUserInfoForm, SubUserEditForm, GenerateQrcode
from uline.model.uline.base import uline_session
from uline.model.uline.user import MchSubUser, MchUserMchSubUser
from datetime import timedelta
from datetime import datetime
from uline.public.permit import check_permission


class SubUserIndexHandler(ChainAdminHandler):
    """点击链接,处理子账户索引请求"""

    @authenticated
    @check_permission
    def prepare(self):
        self.form = SubUserIndexForm(self)
        self.page_index = int(self.get_argument("p", 1))

    def get(self):
        if not self.form.validate() and self.form.status.data is not None:
            self.redirect('/chain/settings/sub_user')
            return

        with self.db.get_db() as cur:
            sub_users, total_number = self.get_employees(cur)
        navigate_html = self.get_navigate_html(total_number)

        self.render('chain/system_settings/csSubUserIndex.html',
                    navigate_html=navigate_html, data=sub_users, form=self.form,
                    total_num=total_number, QR_SCAN_URL=QR_SCAN_URL, dt_id=self.current_user)

    def get_employees(self, cur):

        status = self.form.status.data or None
        create_at_start = self.form.create_at_start.data or None
        create_at_end = self.form.create_at_end.data or None
        mch_sub_name = self.form.mch_sub_name.data or None

        create_at_end = create_at_end + \
            timedelta(days=1) if create_at_end else datetime.now()
        if not create_at_start:
            create_at_start = "2010-01-01 00:00:00"

        query = """select
                    mch_subuser.mch_sub_id,
                    mch_subuser.mch_sub_name,
                    mch_subuser.login_name,
                    mch_subuser.status,
                    mch_subuser.create_at,
                    mch_subuser.wx_id,
                    mch_subuser.wx_open_id,
                    mii.mch_shortname
                    from mch_subuser
                    inner join mch_user_mch_subuser as mums on mch_subuser.mch_sub_id = mums.mch_sub_id
                    left join mch_inlet_info as mii on mii.mch_id = mums.mch_id
                    where mums.dt_id = %(chain_id)s
                    and(mch_subuser.status = %(status)s or %(status)s is null)
                    and(mch_subuser.mch_sub_name::VARCHAR ~ %(mch_sub_name)s or %(mch_sub_name)s is null)
                    AND (mch_subuser.create_at BETWEEN %(create_at_start)s::TIMESTAMP AND %(create_at_end)s::TIMESTAMP OR %(create_at_start)s IS NULL OR %(create_at_end)s IS NULL );
                    """
        cur.execute(
            query, {'chain_id': self.current_user, 'status': status, 'mch_sub_name': mch_sub_name, 'create_at_start': create_at_start, 'create_at_end': create_at_end})
        ret = cur.fetchall()
        ret, total_number = self.deal_ret(ret)
        return ret, total_number

    def deal_ret(self, ret):
        sub_range = defaultdict(list)

        for x in ret:
            if not sub_range[x[0]]:
                sub_range[x[0]].extend(x)
            else:
                if x[7]:
                    cs_name = sub_range[x[0]][7]
                    sub_range[x[0]][7] = ','.join(
                        [cs_name, x[7]]) if cs_name else x[7]
        details = sub_range.values()

        no_right = [x for x in details if x[3] == 2]
        no_rights = sorted(
            no_right, key=lambda tuple_e: tuple_e[4], reverse=True)

        have_right = [x for x in details if x[3] == 1]
        have_rights = sorted(
            have_right, key=lambda tuple_e: tuple_e[4], reverse=True)

        have_rights.extend(no_rights)
        employee = have_rights[(
            self.page_index - 1) * 10:self.page_index * 10]

        return employee, len(details)


class SubUserAddHandler(ChainAdminHandler):
    """处理子账户添加请求"""

    @authenticated
    def prepare(self):
        self.form = SubUserAddForm(self)
        self.form.dt_id = self.current_user

    @gen.coroutine
    def get(self):

        query = """select mch_shortname, mch_id from mch_inlet_info where cs_id = %(cs_id)s;"""
        with self.db.get_db() as cur:
            cur.execute(query, {'cs_id': self.current_user})
            ret = cur.fetchall()
        response = common.scc_rsp(code=200, msg='ok')
        response['data'] = [
            dict(zip(['mch_shortname', 'mch_id'], list(x))) for x in ret]
        self.write(response)
        return

    @gen.coroutine
    def post(self):
        """
        创建新的子账户
        """
        mch_sub_name = self.form.mch_sub_name.data
        login_name = self.form.login_name.data
        email = self.form.email.data
        phone = self.form.phone.data
        password = yield common.bcrypt_pwd(str(self.form.phone.data))

        if not self.form.validate():
            response = common.f_rsp(code=500, msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            self.finish()
            return

        try:
            new_sub_user = MchSubUser(
                mch_sub_name=mch_sub_name,
                login_name=login_name,
                email=email,
                phone=phone,
                password=password,
                status=1,
            )
            uline_session.add(new_sub_user)
            uline_session.commit()

            query_sub_id = "select mch_sub_id from mch_subuser where login_name = %s;"
            mch_sub_id = self.db.selectSQL(query_sub_id, (login_name,))

            insert_mch_id_sub_id = "insert into mch_user_mch_subuser (mch_id,mch_sub_id,dt_id) VALUES (%s,%s,%s);"
            insert_no_mch_id = "insert into mch_user_mch_subuser (mch_sub_id,mch_id,dt_id) VALUES (%s,null,%s);"

            mch_ids = json.loads(self.get_argument('mch_id'))
            if mch_ids:
                for mch_id_item in list(mch_ids):
                    self.db.executeSQL(insert_mch_id_sub_id,
                                       (mch_id_item, mch_sub_id[0], self.current_user))
            else:
                self.db.executeSQL(
                    insert_no_mch_id, (mch_sub_id[0], self.current_user))
            response = common.scc_rsp(code=200, msg='ok')

        except Exception as e:
            log.exception.exception(e)
            response = common.scc_rsp(code=406, msg='fail')

        self.write(response)
        return


class SubUserInfoHandler(ChainAdminHandler):
    """查询子账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserInfoForm(self)
        self.form.dt_id = self.current_user

    @gen.coroutine
    def get(self):
        if not self.form.validate():
            response = common.f_rsp(msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            self.finish()
            return

        field = ['login_name', 'mch_sub_name', 'phone',
                 'email', 'wx_id', 'status']
        profile = dict(zip(field, list(self.get_ret_profile())))

        all_cs = "select mch_shortname,mch_id  from mch_inlet_info where cs_id = %s;"
        ret = self.db.selectSQL(
            all_cs, (int(self.current_user),), fetchone=False)

        right_cs = self.get_ret_cs_name()
        left_cs = list(set(ret) - set(right_cs))
        right_cs_name = [dict(zip(['mch_shortname', 'mch_id'], list(x)))
                         for x in right_cs]
        left_cs_name = [dict(zip(['mch_shortname', 'mch_id'], list(x)))
                        for x in left_cs]

        response = common.scc_rsp(code=200, msg='ok')
        response.update(
            {'profile': profile, 'left_cs_name': left_cs_name, 'right_cs_name': right_cs_name})
        self.write(response)
        return

    def get_ret_profile(self):
        query_profile = "select login_name, mch_sub_name, phone, email, wx_id, status from mch_subuser where mch_sub_id = %s;"
        ret_profile = self.db.selectSQL(
            query_profile, (self.form.mch_sub_id.data,))
        return ret_profile

    # 获取已有门店简称
    def get_ret_cs_name(self):
        cs_name_query = """select mii.mch_shortname, mii.mch_id from mch_user_mch_subuser as mums inner join mch_inlet_info as mii on mii.mch_id = mums.mch_id where mums.mch_sub_id = %s"""
        ret_cs_name = self.db.selectSQL(
            cs_name_query, (self.form.mch_sub_id.data,), fetchone=False)
        return ret_cs_name


class SubUserEditHandler(SubUserInfoHandler):
    """编辑子账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserEditForm(self)
        self.form.dt_id = self.current_user

    @gen.coroutine
    def post(self):
        if not self.form.validate():
            response = common.f_rsp(msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            return
        try:

            query = """update mch_subuser
                      set mch_sub_name=%s,phone=%s,email=%s,status=%s where mch_sub_id = %s"""
            self.db.executeSQL(query, (
                self.form.mch_sub_name.data, self.form.phone.data, self.form.email.data, self.form.status.data, self.form.mch_sub_id.data))

            ret_cs_id, ret_cs_start = self.get_cs_status()
            if ret_cs_start:
                self.add_new_css(list())
            else:
                cs_ids = [str(cs_id[0])
                          for cs_id in ret_cs_id if cs_id[0] is not None]
                self.add_new_css(cs_ids)
            # 如果员工门店更新为不属于任何一个门店,则取消绑定.
            ret_cs_end = self.get_cs_status()
            if ret_cs_end[1]:
                uline_session.query(MchSubUser.wx_open_id, MchSubUser.wx_id).filter(
                    MchSubUser.mch_sub_id == self.form.mch_sub_id.data).update({"wx_open_id": None, "wx_id": None})
                uline_session.commit()

            response = common.scc_rsp()

        except Exception as err:
            log.exception.exception(err)
            response = common.scc_rsp(code=406, msg='fail')

        self.write(response)
        return

    def add_new_css(self, old_css):

        cs = set(old_css) if old_css else set()
        add_new = list(set(json.loads(self.form.mch_id.data)) - cs)

        if add_new:
            if not old_css:
                self.db.executeSQL("update mch_user_mch_subuser set mch_id = %s where mch_sub_id =%s and mch_id is null;", (
                    add_new[-1], self.form.mch_sub_id.data))
                add_new.pop()
            if add_new:
                for new in add_new:
                    self.db.executeSQL("""insert into mch_user_mch_subuser
                    (mch_id,mch_sub_id,dt_id) VALUES (%s,%s,%s);""", (int(new), int(self.form.mch_sub_id.data), self.current_user))

        if old_css:
            dele_cs = json.loads(self.form.mch_id.data)
            deles = list(set(old_css) - set(dele_cs))
            if deles:
                if not dele_cs:
                    self.db.executeSQL(
                        "update mch_user_mch_subuser set mch_id = null where mch_sub_id =%s and mch_id=%s;", (self.form.mch_sub_id.data, deles[-1]))
                    deles.pop()
                if deles:
                    for dele in deles:
                        delete_cs = """ delete from mch_user_mch_subuser
                                                        where mch_id=%s AND mch_sub_id=%s;"""
                        self.db.executeSQL(
                            delete_cs, (int(dele), int(self.form.mch_sub_id.data)))
        return
# 获取临时二维码

    def get_cs_status(self):
        ret_cs_id = uline_session.query(MchUserMchSubUser.mch_id).filter(
            MchUserMchSubUser.mch_sub_id == self.form.mch_sub_id.data).all()
        return [ret_cs_id, (len(ret_cs_id) == 1 and not ret_cs_id[0][0])]
