# -*- coding: utf-8 -*-
from uline.backend.__init__ import *
import datetime
from os import path, remove
from uline.public import log

cur_dir = path.dirname(path.dirname(path.abspath(__file__)))


@app.task
def delete_overdue_report():
    static_path = path.normpath(path.join(cur_dir, '../static/downloads/'))
    ret = find_record_seven_days_ago()
    for user_id,  filename, in ret:
        update_status_and_delete_file(user_id, filename, static_path)


def find_record_seven_days_ago():
    today = datetime.datetime.now()
    seven_day_ago = today - datetime.timedelta(days=7)
    query = """select user_id, file from order_download_info where update_at<%(seven_day_ago)s::TIMESTAMP
               and status!=5;"""
    ret = db.selectSQL(query, {
        'seven_day_ago': seven_day_ago,
    }, fetchone=False)
    return ret


def update_status_and_delete_file(user_id, filename, static_path):
    with db.get_db() as cur:
        try:
            query = """UPDATE order_download_info SET status=5 where user_id=%s AND file=%s"""
            cur.execute(query, (user_id, filename))
            file_path = path.join(static_path, str(user_id), filename)
            remove(file_path)
        except Exception as err:
            log.exception.error(err)
            cur.connection.rollback()
        else:
            cur.close()
            cur.connection.commit()


if __name__ == "__main__":
    delete_overdue_report()