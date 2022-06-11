from timeit import default_timer as timer


class benchmark(object):

    def __init__(self, logger, msg, fmt="%0.3g"):
        self.msg = msg
        self.fmt = fmt
        self.logger = logger

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, *args):
        t = timer() - self.start
        self.logger.info(("%s : " + self.fmt + " seconds") % (self.msg, t))
        self.time = t
