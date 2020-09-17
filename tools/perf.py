import timeit


class Perf:

    def __init__(self, take_intervals=False):
        self.start = timeit.default_timer()
        if take_intervals:
            self.intervals = list()
        else:
            self.intervals = None

    def elapsed(self):
        hold = timeit.default_timer() - self.start
        if self.intervals is not None:
            self.start = Perf.now()
            self.intervals.append(hold)
        return hold

    @staticmethod
    def now():
        return timeit.default_timer()

    @staticmethod
    def time_elapsed(func, args):
        start_time = Perf.now()
        out = func(args)
        elapsed = Perf.now() - start_time
        return {"out": out, "elapsed": elapsed}
