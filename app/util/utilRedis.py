import redis

class RedisAccess:

    @staticmethod
    def connection(r=None):
        if (r == None):
            return redis.StrictRedis(
                host='127.0.0.1', port=6379, db=0)
        else:
            return r
