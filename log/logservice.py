import logging


class Log():
    def __init__(self, config):
        loglevel = 'DEBUG'
        if 'log' in config.config:
            loglevel = config.config['log'].get('loglevel', 'ERROR')

        logfile = 'yakbee.log'
        self.logger = logging.getLogger('yakbee')
        self.logger.setLevel(self.get_level(loglevel))


        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file = logging.FileHandler(filename=logfile, mode='a')
        file.setLevel(self.get_level(loglevel))
        file.setFormatter(formatter)
        self.logger.addHandler(file)

        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S') #('%(message)s')
        handler = logging.StreamHandler()
        handler.setLevel(self.get_level(loglevel))
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


    def debug(self, str):
        self.logger.debug(str)

    def info(self, str):
        self.logger.info(str)

    def warning(self, str):
        self.logger.warning(str)

    def critical(self, str):
        self.logger.critical(str)

    def error(self, str):
        self.logger.error(str)

    def get_level(cls, level):
        if level == "CRITICAL":
            return logging.CRITICAL
        elif level == "ERROR":
            return logging.ERROR
        elif  level == "WARNING":
            return logging.WARNING
        elif level == "INFO":
            return logging.INFO
        elif level == "DEBUG":
            return logging.DEBUG
        else:
            return logging.NOTSET






