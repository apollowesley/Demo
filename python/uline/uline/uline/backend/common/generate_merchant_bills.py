# -*- coding: utf-8 -*-
from __future__ import division
from os import path, makedirs, remove
import time
import shutil
from uline.backend.__init__ import *
from uline.public import common, log
import zipfile

cur_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@app.task
def generate_zip(user_id, all_csv, num_csvs):

    order_id = common.create_order_id()
    file_name, file_path, static_path, temp_path = general_filename(user_id)
    if num_csvs > 1:
        gen_order_download_info(order_id, user_id, file_name)
    try:
        zip_file = zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED)
        for des_file_list, file_list in all_csv:
            shutil.copy(des_file_list, temp_path)
            temp_file = path.join(temp_path, path.split(des_file_list)[1])
            with open(temp_file, 'r') as rf:
                data = rf.read()
                new_data = data.encode('GB18030', errors='ignore')
            with open(temp_file, 'w') as wf:
                wf.write(new_data)
            zip_file.write(temp_file, arcname=file_list)
            remove(temp_file)
        zip_file.close()
        if num_csvs > 1:
            modify_order_download_info(order_id, 2)
    except Exception as err:
        if num_csvs > 1:
            modify_order_download_info(order_id, 3)
        log.exception.exception(err)
        return {'static_path': False}
    return {'static_path': static_path}


def general_filename(user_id):
    filename = "merchant_bills_" + str(time.time()) + ".zip"
    user_dl_path = path.join(cur_dir, "static/downloads/", str(user_id))
    if not path.exists(user_dl_path):
        makedirs(user_dl_path)
    static_path = path.join("/static/downloads/", str(user_id), filename)
    temp_path = path.join("/var/tmp/", str(user_id))
    if not path.exists(temp_path):
        makedirs(temp_path)
    return filename, path.join(user_dl_path, filename), static_path, temp_path


def gen_order_download_info(order_id, user_id, file_name):
    create_at = update_at = common.timestamp_now()
    query = """insert into order_download_info (order_id, user_id, file, type, status, platform, create_at, update_at)
            values (%s,%s,%s,%s,%s,%s,%s,%s)"""
    db.executeSQL(query, (order_id, user_id, file_name,
                          12, 1, 1, create_at, update_at))


def modify_order_download_info(order_id, status):
    update_at = common.timestamp_now()
    query = """update order_download_info set status=%s,update_at=%s where order_id=%s;"""
    db.executeSQL(query, (status, update_at, order_id))
