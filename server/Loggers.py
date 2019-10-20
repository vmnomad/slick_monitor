from Utils import load_loggers
import logging
import socket
from logging.handlers import RotatingFileHandler


def get_logging_config():
    pass


def get_logger():
    hostname = '127.0.0.1'
    port = '1234'


    logger = logging.getLogger(__name__)
    logger.propagate = False # disables propagation of mylogger to root logger

    logger.setLevel(logging.INFO)
    # set format
    nc_format = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')

    # create nc handler
    nc_handler =Nc_handler(hostname, port, format)

    # set handler's format
    nc_handler.setFormatter(nc_format)

    # set handler's level
    nc_handler.setLevel(logging.INFO)

    # create file handler
    file_handler = RotatingFileHandler('logs/slick_monitor.log',  maxBytes=1000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(nc_format)


    logger.addHandler(nc_handler)
    logger.addHandler(file_handler)
    return logger


class Nc_handler(logging.Handler):
    def __init__(self, hostname, port, format):
        logging.Handler.__init__(self)
        try:          
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((hostname, int(port)))
            self.init = True
        except Exception as error:
            self.init = False
            print('Failed to initialized Nc_handler. Error:', error)

    def emit(self, record):
        if self.init == True:
            log_entry = self.format(record)
            try:
                self.socket.send((log_entry + '\n').encode())
            except Exception as error:
                print('Failed emit. Error:', error)
        else:
            print('Nc_handler is not initialised.')






#class Logger:
    #pass
