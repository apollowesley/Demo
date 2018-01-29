# -*- coding:utf-8 -*-
import json
import requests
from settings import server_port

TEST_PORT = server_port


def execute(url, data):
    url = 'http://127.0.0.1:%s%s' % (TEST_PORT, url)
    print url
    response = requests.post(url, data=json.dumps(data))
    print response
    print response.status_code
    assert response.status_code == 200
    print response.content
    response_list = json.loads(response.content)
    assert response_list['code'] == 200
