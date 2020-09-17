from lib.caching.policy import Policy


class TranscriptCache:

    def __init__(self, policy: Policy):
        self.policy = policy
        self.cache = dict()

    def add(self, key: str, value: object):
        self.cache[key] = value

        evicted = self.policy.evict()
        if evicted is not None:
            return self.cache.pop(evicted)

    def get(self, key):
        resolution = None
        cached = self.policy.resolve(key)
        if cached:
            resolution = self.cache[key]
        return resolution
