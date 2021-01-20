from threading import Lock

from lib.caching.fingerprint import is_similar
from lib.caching.policy import Policy


class TranscriptCache:
    def __init__(self, policy: Policy):
        self.policy = policy
        self.cache = dict()
        self.cache_lk = Lock()

    def add(self, key: str, value: object) -> None:
        if key is not None:
            self.cache[key] = value
        # evicted = self.policy.evict(key)
        # if evicted is not None:
        #     return self.cache.pop(evicted)
        # return {}

    def get(self, fp_key) -> object:
        resolution = {}
        # cached = self.policy.resolve(key)
        # if cached:
        # resolution = self.cache[key]
        self.cache_lk.acquire()
        cache_instance = self.cache.copy()
        self.cache_lk.release()
        for key in cache_instance:
            match = is_similar(key, fp_key)
            if match:
                return cache_instance[key]
        return resolution
