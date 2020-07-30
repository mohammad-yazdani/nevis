import timeit


def time_elapsed(func, args):
    start_time = timeit.default_timer()
    out = func(args)
    elapsed = timeit.default_timer() - start_time
    return {"out": out, "elapsed": elapsed}
