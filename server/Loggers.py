import logging
import socket
from logging.handlers import RotatingFileHandler
import sqlite3
import json
from queue import Queue
import builtins
from logging.handlers import QueueHandler
LOGGING_FORMAT = logging.Formatter(' %(asctime)s - %(levelname)s - %(name)s - %(module)s - %(message)s')

# setting up module logger
loggers_logger = logging.getLogger(__name__)
loggers_logger.propagate = False
loggers_logger.setLevel(logging.DEBUG)

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
            loggers_logger.debug('Netcat handler is initialized')
        except Exception as error:
            self.init = False
            loggers_logger.error('Failed to initialized Nc_handler. Error:'.format(error))

    def __repr__(self):
        return 'Netcat Handler: {}, {}'.format(self.hostname, self.port)

    def update(self, hostname, port, logging_level):
        if self.hostname != hostname or \
           self.port != port:
            self.socket.close
            self.hostname = hostname
            self.port = port          
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, int(self.port)))
            loggers_logger.debug('Updated Netcat Handler. New hostname: {}, new port: {}'.format(self.hostname, self.port))
        self.setLevel(logging_level)
        loggers_logger.debug('Updated Netcat Handler. New logging level: {}'.format(logging_level))

    def emit(self, record):
        if self.init == True:
            log_entry = self.format(record)
            try:
                self.socket.send((log_entry + '\n').encode())
            except Exception as error:
                loggers_logger.error('Failed emit. Error: {}'.format(error))
        else:
            loggers_logger.warning('Failed emit. Error: {}'.format(error))

def get_logging_config():

    conn = sqlite3.connect('server.db', timeout=5.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * from LOGGERS")
    result = cursor.fetchall()

    loggers_configuration = {}
    for item in result:
        loggers_configuration[item['type']] =json.loads(item['settings'])
    loggers_logger.debug('Loaded loggers configuration')
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
    try:
        if log_type == 'console' and settings['enabled'] == 1:
            return get_console_handler(settings)
        elif log_type == 'file' and settings['enabled'] == 1:
            return get_file_handler(settings)
        elif log_type == 'netcat' and settings['enabled'] == 1:
            return get_netcat_handler(settings)
        else:
            loggers_logger.error('Cannot find logging handler type: {}'.format(log_type))
            return None
    except:
        return None

builtins.log_queue = Queue(-1)
def get_queue_logger(log_level, module_name):
    q_handler = QueueHandler(log_queue)
    q_logger = logging.getLogger(module_name)
    q_logger.propagate = False 
    q_logger.addHandler(q_handler)
    q_logger.setLevel(log_level)
    return q_logger

def get_logger():
    logger = logging.getLogger(__name__)
    logger.propagate = False # disables propagation of mylogger to root logger
    logger.setLevel(logging.DEBUG)

    try:
        logging_config = get_logging_config()
        for log_type, settings in logging_config.items():
            log_handler = get_logging_handler(log_type, settings)
            if log_handler != None:
                logger.addHandler(log_handler)
                logger.info('{} logging is enabled'.format(log_type.capitalize()))
            
    except Exception as error:
        print('Failed to initialise logging handler {}. Error: {}'.format(log_type, error))

    return logger

# temp disabled
def update_logger(logger):
    handlers = logger.handlers
    new_config = logging_config = get_logging_config()
    for i in range(len(handlers)):
        #print(handlers[i].name)
        h_name = handlers[i].name
        if h_name != 'netcat_handler':
            handlers[i].setLevel = new_config[h_name.split('_')[0]]['logging_level']
            #print('Setting Handler: {} with new logging level: {}'.format(h_name, new_config[h_name.split('_')[0]]['logging_level']))
        else:
            #print(new_log_level)
            new_hostname = new_config[h_name.split('_')[0]]['hostname']
            new_port = new_config[h_name.split('_')[0]]['port']
            new_logging_level = new_config[h_name.split('_')[0]]['logging_level']
            handlers[i].update(new_hostname, new_port, new_logging_level)
            #print('Setting Handler: {} with new logging level: {}'.format(h_name, new_config[h_name.split('_')[0]]['logging_level']))
