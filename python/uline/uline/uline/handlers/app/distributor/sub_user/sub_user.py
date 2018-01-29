# -*- coding: utf-8 -*-

from datetime import timedelta
from datetime import datetime

from tornado import gen
from tornado.web import authenticated, HTTPError
from uline.public import common, log

from uline.handlers.baseHandlers import DtAdminHandler
from uline.settings import QR_SCAN_URL

from uline.model.uline.user import DtSubUser
from uline.model.uline.base import uline_session

from .form import SubUserIndexForm, SubUserAddForm, SubUserInfoForm, SubUserEditForm

INDEX_PAGE_SIZE = 10


class SubUserSearchHandler(DtAdminHandler):
    """处理查询子账户的请求"""

    @authenticated
    def get(self):
        """
        根据名字获取子账户列表
        """
        dt_id = self.current_user
        name = self.get_argument('q', None)
        all = self.get_argument('all', None)

        query = uline_session.query(DtSubUser.dt_sub_id.label('id'), DtSubUser.dt_sub_name).\
            filter(DtSubUser.dt_user_dt_id == dt_id)

        if name:
            query = query.filter(DtSubUser.dt_sub_name.contains(name))

        if not all:
            query = query.filter(DtSubUser.status == 1)
        sub_users = query.limit(INDEX_PAGE_SIZE).all()

        data = [_model._asdict() for _model in sub_users]
        response = common.scc_rsp(code=200, msg='success')
        response['data'] = data
        response['total_count'] = len(data)
        self.write(response)


class SubUserIndexHandler(DtAdminHandler):
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
        self.render('distributor/sub_user/subUserIndex.html',
                    navigate_html=navigate_html, data=sub_users, form=self.form,
                    total_num=total_number, QR_SCAN_URL=QR_SCAN_URL, dt_id=self.current_user)

    def get_sub_users(self, page_index):
        """根据条件获取对应子账户"""

        page_size = int(self.get_argument("page_size", INDEX_PAGE_SIZE))

        query = uline_session.query(DtSubUser)

        query = query.filter(DtSubUser.dt_user_dt_id == self.current_user)

        if self.form.create_at_start.data:
            query = query.filter(DtSubUser.create_at >= self.form.create_at_start.data)

        create_at_end = self.form.create_at_end.data
        if create_at_end:
            # 结束时间需要加一天，以包括结束当天的查询
            create_at_end += timedelta(days=1)
            query = query.filter(DtSubUser.create_at <= create_at_end)

        if self.form.status.data:
            query = query.filter(DtSubUser.status == self.form.status.data)

        if self.form.dt_sub_name.data:
            query = query.filter(DtSubUser.dt_sub_name.contains(self.form.dt_sub_name.data))

        total_number = query.count()

        # 默认最新修改的排在前面
        query = query.order_by(DtSubUser.update_at.desc()).\
            limit(page_size).offset((page_index - 1) * page_size)

        sub_users = query.all()

        return sub_users, total_number


class SubUserAddHandler(DtAdminHandler):
    """处理子账户请求"""

    @authenticated
    def prepare(self):
        self.form = SubUserAddForm(self)
        self.form.dt_id = self.current_user

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
        new_sub_user = DtSubUser(
            dt_user_dt_id=self.current_user,
            dt_sub_name=self.form.dt_sub_name.data,
            login_name=self.form.login_name.data,
            email=self.form.email.data,
            phone=self.form.phone.data,
            password=password,
            status=self.form.status.data,
        )
        uline_session.add(new_sub_user)
        uline_session.commit()

        response = common.scc_rsp(code=200)
        self.write(response)


class SubUserInfoHandler(DtAdminHandler):
    """查询子账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserInfoForm(self)
        self.form.dt_id = self.current_user

    def get(self):
        if not self.form.validate():
            response = common.f_rsp(msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            self.finish()
            return

        dt_sub_id = self.form.dt_sub_id.data
        sub_user = uline_session.query(DtSubUser).filter(DtSubUser.dt_sub_id == dt_sub_id).\
            filter(DtSubUser.dt_user_dt_id == self.current_user).one()

        response = common.scc_rsp()
        response['data'] = sub_user.to_dict(excluded=('password', 'api_key'))
        self.write(response)


class SubUserEditHandler(DtAdminHandler):
    """查询子账户的详细信息"""

    @authenticated
    def prepare(self):
        self.form = SubUserEditForm(self)
        self.form.dt_id = self.current_user

    def post(self):
        if not self.form.validate():
            response = common.f_rsp(msg='Invalid arguments')
            response['data'] = self.form.errors
            self.write(response)
            return self.finish()

        dt_sub_id = self.form.dt_sub_id.data
        sub_user = uline_session.query(DtSubUser).filter(DtSubUser.dt_sub_id == dt_sub_id)

        sub_user.update({
            'dt_sub_name': self.form.dt_sub_name.data,
            'email': self.form.email.data,
            'phone': self.form.phone.data,
            'status': self.form.status.data,
            'update_at': datetime.now(),
        })
        uline_session.commit()
        response = common.scc_rsp()
        self.write(response)
