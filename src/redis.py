import redis


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisClient(metaclass=Singleton):
    def __init__(self, host="localhost", password=None):
        self.pool = redis.ConnectionPool(host=host, password=password)

    @property
    def conn(self):
        if not hasattr(self, "_conn"):
            self.get_connection()
        return self._conn

    def get_connection(self):
        self._conn = redis.Redis(connection_pool=self.pool, decode_responses=True)

    # For testing
    def clear(self):
        if not hasattr(self, "_conn"):
            raise Exception("RedisClient is not initialized")
        self._conn.flushdb()
