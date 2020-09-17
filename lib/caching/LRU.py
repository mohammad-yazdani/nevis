from lib.caching.policy import Policy


class LRU(Policy):

    def __init__(self, window_size: int):
        super().__init__(window_size)
        self.lr_list = dict()
        self.epoch = 0

    def resolve(self, hash_key: str):
        self.epoch += 1
        in_cache = hash_key in self.lr_list

        self.lr_list[hash_key] = self.epoch
        return in_cache

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
