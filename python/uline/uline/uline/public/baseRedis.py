# -*- coding:utf-8 -*-


class RedisClient(object):

    def __init__(self, client, **kwargs):
        self.client = client
        self.kwargs = kwargs

    # redis常规操作
    def set(self, name, value):
        return self.client.set(name, value)

    def get(self, name):
        return self.client.get(name)

    def hmset(self, name, value):
        return self.client.hmset(name, value)

    def hgetall(self, name):
        return self.client.hgetall(name)

    def hget(self, name, code):
        return self.client.hget(name, code)

    def setex(self, name, code, time):
        return self.client.setex(name, code, time)

    def hset(self, name, code, value):
        return self.client.hset(name, code, value)

    def hdel(self, name, code):
        return self.client.hdel(name, code)

    def publish(self, room, msg):
        return self.client.publish(room, msg)

    def delete(self, name):
        return self.client.delete(name)

    def exists(self, name):
        return self.client.exists(name)

    def hexists(self, name, code):
        return self.client.hexists(name, code)
    # redis常规操作
