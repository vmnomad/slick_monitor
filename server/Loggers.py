import logging
import socket
from logging.handlers import RotatingFileHandler
import sqlite3
import json

LOGGING_FORMAT = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')


class Netcat_handler(logging.Handler):
    def __init__(self, hostname, port):
        logging.Handler.__init__(self)
        try:
            self.name = 'netcat_handler'
            self.hostname = hostname
            self.port = port          
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, int(self.port)))
            self.init = True
        except Exception as error:
            self.init = False
            print('Failed to initialized Nc_handler. Error:', error)
    def __repr__(self):
        return 'Netcat Handler: {}, {}'.format(self.hostname, self.port)

    def update(self, settings):
        pass


    def emit(self, record):
        if self.init == True:
            log_entry = self.format(record)
            try:
                self.socket.send((log_entry + '\n').encode())
            except Exception as error:
                print('Failed emit. Error:', error)
        else:
            print('Nc_handler is not initialised.')

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
    c_handler.name = 'console_handler'
    return c_handler

def get_file_handler(settings):
    file_size = int(settings['file_size']) * 1024 * 1024
    file_number = int(settings['file_number'])
    f_handler = RotatingFileHandler('logs/slick_monitor.log',  maxBytes=file_size, backupCount=file_number)
    f_handler.setLevel(settings['logging_level'])
    f_handler.setFormatter(LOGGING_FORMAT)
    f_handler.name = 'file_handler'
    return f_handler

def get_netcat_handler(settings):
    hostname = settings['hostname']
    port = settings['port']
    nc_handler = Netcat_handler(hostname, port)
    nc_handler.setFormatter(LOGGING_FORMAT)
    nc_handler.setLevel(settings['logging_level'])
    return nc_handler

def get_logging_handler(log_type, settings):
    if log_type == 'console' and settings['enabled'] == 1:
        return get_console_handler(settings)
    elif log_type == 'file' and settings['enabled'] == 1:
        return get_file_handler(settings)
    elif log_type == 'netcat' and settings['enabled'] == 1:
        return get_netcat_handler(settings)
    else:
        logging.info('Cannot find logging handler type: {}'.format(log_type))
        return None

def update_logging_handler(log_type, settings):
    if log_type == 'console' and settings['enabled'] == 1:
        return get_console_handler(settings)
    elif log_type == 'file' and settings['enabled'] == 1:
        return get_file_handler(settings)
    elif log_type == 'netcat' and settings['enabled'] == 1:
        return get_netcat_handler(settings)
    else:
        logging.info('Cannot find logging handler type: {}'.format(log_type))
        return None

def get_logger():
    logger = logging.getLogger(__name__)
    logger.propagate = False # disables propagation of mylogger to root logger
    logger.setLevel(logging.INFO)

    try:
        logging_config = get_logging_config()
        for log_type, settings in logging_config.items():
            print('Logger: {}, Enabled: {}'.format(log_type, settings['enabled']))

            log_handler = get_logging_handler(log_type, settings)

            if log_handler != None:
                logger.addHandler(log_handler)
            
    except Exception as error:
        print('Failed to initialise logging handler {}. Error: {}'.format(log_type, error))

    return logger

def update_logger(logger):
    handlers = logger.handlers
    for i in range(len(handlers)):
        print(handlers[i].name)