import logging
import socket
from logging.handlers import RotatingFileHandler
import sqlite3
import json

LOGGING_FORMAT = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')

def get_logging_config():

    conn = sqlite3.connect('server.db', timeout=5.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * from LOGGERS")
    result = cursor.fetchall()

    loggers_configuration = {}
    for item in result:
        loggers_configuration[item['type']] =json.loads(item['settings'])
    return loggers_configuration


def get_console_handler(settings):
    c_handler = logging.StreamHandler()
    c_handler.setLevel(settings['logging_level'])
    c_handler.setFormatter(LOGGING_FORMAT)
    return c_handler

def get_file_handler(settings):
    file_size = int(settings['file_size']) * 1024 * 1024
    file_number = int(settings['file_number'])
    f_handler = RotatingFileHandler('logs/slick_monitor.log',  maxBytes=file_size, backupCount=file_number)
    f_handler.setLevel(settings['logging_level'])
    f_handler.setFormatter(LOGGING_FORMAT)
    return f_handler

def get_netcat_handler(settings):
    hostname = settings['hostname']
    port = settings['port']
    nc_handler = Nc_handler(hostname, port)
    nc_handler.setFormatter(LOGGING_FORMAT)
    nc_handler.setLevel(settings['logging_level'])
    return nc_handler

def get_logger():

    logger = logging.getLogger(__name__)
    logger.propagate = False # disables propagation of mylogger to root logger
    logger.setLevel(logging.INFO)

    try:
        logging_config = get_logging_config()
        for log_type, settings in logging_config.items():
            print('Logger: {}, Enabled: {}'.format(log_type, settings['enabled']))
            if log_type == 'console' and settings['enabled'] == 1:
                logger.addHandler(get_console_handler(settings))
            elif log_type == 'file' and settings['enabled'] == 1:
                logger.addHandler(get_file_handler(settings))
            elif log_type == 'netcat' and settings['enabled'] == 1:
                logger.addHandler(get_netcat_handler(settings))
    except Exception as error:
        print('Failed to initialise logging handler {}. Error: {}'.format(log_type, error))

    return logger


class Nc_handler(logging.Handler):
    def __init__(self, hostname, port):
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

