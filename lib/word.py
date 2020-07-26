class Word:

    def __init__(self, value, timestamp, tags=None):
        self.value = value
        self.timestamp = timestamp
        self._tags = tags
        if self._tags is None:
            self._tags = dict()

    def add_tag(self, key, val):
        self._tags[key] = val

    def get_tag(self, key):
        return self._tags[key]

    def __str__(self):
        val = "Word: " + str(self.value) + ", "
        timestamp = "Timestamp: " + str(self.timestamp) + ", "
        tags = "Tags: " + str(self._tags)

        return val + timestamp + tags
