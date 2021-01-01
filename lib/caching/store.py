from lib.caching.policy import Policy
from threading import Thread

class TranscriptCache:
    def __init__(self, policy: Policy):
        self.policy = policy
        self.cache = dict()

    def add(self, key: str, value: object) -> object:
        if key is None:
            return {}
        
        self.cache[key] = value

        evicted = self.policy.evict()
        if evicted is not None:
            return self.cache.pop(evicted)
        return {}

    def get(self, key) -> object:
        resolution = {}
        cached = self.policy.resolve(key)
        if cached:
            resolution = self.cache[key]
        return resolution
