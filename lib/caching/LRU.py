from lib.caching.fingerprint import is_similar
from lib.caching.policy import Policy


class LRU(Policy):

    def __init__(self, window_size: int):
        super().__init__(window_size)
        self.lr_list = dict()
        self.epoch = 0

    def resolve(self, fp_key: str):
        self.epoch += 1

        # This is normal dictionary usage, but we are using fingerprints
        # in_cache = hash_key in self.lr_list
        curr_keys = self.lr_list.keys()
        for key in curr_keys:
            if is_similar(fp_key, key):
                self.lr_list[key] = self.epoch
                return True
        return False

    def evict(self):
        if len(self.lr_list) <= 50:
            return None
        last = self.epoch
        last_key = None
        for k in self.lr_list:
            if self.lr_list[k] < last:
                last = self.lr_list[k]
                last_key = k
        self.lr_list.pop(last_key)
        return last_key
