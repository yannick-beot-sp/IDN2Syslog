class Helper(object):
    def __init__(self, logger=None):
        self.logger = logger


    def log_error(self, msg):
        print(msg)
        if self.logger:
            self.logger.error(msg)

    def log_info(self, msg):
        print(msg)
        if self.logger:
            self.logger.info(msg)

    def log_debug(self, msg):
        print(msg)
        if self.logger:
            self.logger.debug(msg)



