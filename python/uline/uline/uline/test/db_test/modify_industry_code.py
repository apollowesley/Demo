# -*- coding: utf-8 -*-
from uline.public.baseDB import DbClient

db = DbClient()


def get_dt_old_wx_code():
    query = """select
            industry_uline_info.industry_code,
            industry_uline_info.ali_ind_code,
            dt_inlet_info.old_ind_code,
            dt_inlet_info.dt_id
            from dt_inlet_info
            inner join industry_uline_info on industry_uline_info.wx_ind_code=dt_inlet_info.old_ind_code
            where dt_inlet_info.old_ind_code is not null
            and dt_inlet_info.u_ind_code is null
            and industry_uline_info.status=1;"""
    ret = db.selectSQL(query, fetchone=False)
    return ret


def update_dt_user_code(datas):
    for data in datas:
        query = """update dt_inlet_info set u_ind_code=%s,ali_ind_code=%s,wx_ind_code=%s where dt_id=%s;"""
        db.executeSQL(query, (data[0], data[1], data[2], data[3]))


def get_mch_old_wx_code():
    query = """select
            mch_id,
            old_ind_code
            from mch_inlet_info
            where old_ind_code is not null
            and u_ind_code is null;"""
    ret = db.selectSQL(query, fetchone=False)
    return ret


def gen_mch_ind_code(datas):
    mch_owc = [list(i) for i in datas]
    mch_new_ind_code = list()
    for data in mch_owc:
        query = """select
                industry_code,
                ali_ind_code,
                wx_ind_code
                from industry_uline_info
                where wx_ind_code=%s and status=1;"""
        ret_ind = db.selectSQL(query, (data[1],))
        if ret_ind:
            data.extend(list(ret_ind))
            mch_new_ind_code.append(data)
    return mch_new_ind_code


def update_mch_user_code(datas):
    for data in datas:
        query = """update
                mch_inlet_info
                set
                u_ind_code=%s,
                ali_ind_code=%s,
                wx_ind_code=%s
                where mch_id=%s;"""
        db.executeSQL(query, (data[2], data[3], data[4], data[0]))


def update_special_code():
    query = """update dt_inlet_info set u_ind_code='161215010100306',ali_ind_code='2016062900190357',wx_ind_code='310' where dt_id=10000016270;"""
    db.executeSQL(query)

    query = """update mch_inlet_info
               set u_ind_code='161215010100351',ali_ind_code='2016062900190248',wx_ind_code='277'
               where mch_id in (100000193968,100000197950,100000039166,100000028752,100000195443,100000196526,100000005476,100000032523,100000197816,100000001136,100000172832,100000006390,100000195588,100000003330,100000199860,100000158317)"""
    db.executeSQL(query)

    query = """update mch_inlet_info
               set u_ind_code='161215010100218',ali_ind_code='2016062900190247',wx_ind_code='42'
               where mch_id in (100000007919,100000008440,100000008397,100000008224,100000008155,100000008066)"""
    db.executeSQL(query)

    query = """update mch_inlet_info
               set u_ind_code='161215010100570',ali_ind_code='2016062900190247',wx_ind_code='143'
               where mch_id=100000187121;"""
    db.executeSQL(query)

    query = """update mch_inlet_info
           set u_ind_code='161215010100343',ali_ind_code='2016062900190234',wx_ind_code='60'
           where mch_id=100000014351;"""
    db.executeSQL(query)


if __name__ == '__main__':
    print('start update dt user')
    ret = get_dt_old_wx_code()
    update_dt_user_code(ret)
    print('end update dt user')

    print('start update mch user')
    ret = get_mch_old_wx_code()
    mch_new_ind_code = gen_mch_ind_code(ret)
    update_mch_user_code(mch_new_ind_code)
    print('end update dt user')

    print('start update special user')
    update_special_code()
    print('end update special user')
