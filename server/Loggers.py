import logging
import socket
from logging.handlers import RotatingFileHandler
import sqlite3
import json
from queue import Queue
import builtins
from logging.handlers import QueueHandler
from colorlog import ColoredFormatter
import os


COLOR_LOGGING_FORMAT = ColoredFormatter(' %(asctime)s | %(log_color)s%(levelname)-5s%(reset)s | %(module)-7s | %(log_color)s%(message)s%(reset)s')
LOGGING_FORMAT = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s - %(module)s')


# Database Name
db_folder = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
db_name = 'slick_monitor_db.sqlite3'
DB_PATH = os.path.join(db_folder, db_name)

def get_logging_config():

    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * from LOGGERS")
    result = cursor.fetchall()

    loggers_configuration = {}
    for item in result:
        loggers_configuration[item['type']] =json.loads(item['settings'])
    loggers_logger.debug('Loaded loggers configuration')
    return loggers_configuration


# setting up local logger
loggers_logger = logging.getLogger(__name__)
loggers_logger.propagate = False
logging_config = get_logging_config()
loggers_logger.setLevel(logging.DEBUG)
s_handler = logging.StreamHandler()
s_handler.setFormatter(COLOR_LOGGING_FORMAT)
level = logging_config['console']['logging_level']
s_handler.setLevel(level)
loggers_logger.addHandler(s_handler)

class Netcat_handler(logging.Handler):
    def __init__(self, hostname, port):
        logging.Handler.__init__(self)
        try:
            self.name = 'netcat_handler'
            self.hostname = hostname
            self.port = port          
            self.nc_connect()
            loggers_logger.debug('Netcat handler is initialized')
        except Exception as error:
            self.init = False
            loggers_logger.error('Failed to initialized Nc_handler. Error: {}'.format(error))

    def nc_connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, int(self.port)))
            self.init = True
        except Exception as error:
            self.init = True
            loggers_logger.error('Failed to connect to {} on port {}. Error: {}'.format(self.hostname, self.port, error))


    def __repr__(self):
        return 'Netcat Handler: {}, {}'.format(self.hostname, self.port)

    def update(self, hostname, port):
        if self.hostname != hostname or \
           self.port != port:
            self.socket.close
            self.hostname = hostname
            self.port = port          
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.hostname, int(self.port)))
            loggers_logger.debug('Updated Netcat Handler. New hostname: {}, new port: {}'.format(self.hostname, self.port))

    def emit(self, record):
        if self.init == True:
            log_entry = self.format(record)
            try:
                self.socket.send((log_entry + '\n').encode())
            except BrokenPipeError as error:
                self.nc_connect()
                #self.socket.send((log_entry + '\n').encode())
                loggers_logger.error('Failed to send log to netcat host. Please ensure netcat is configured on host {} , port {}. Error: {}'.format(self.hostname, self.port, error))
            except Exception as error:
                loggers_logger.error('Failed emit. Error: {}'.format(error))
        else:
            loggers_logger.warning('Failed emit. Netcat logger is not initialized.')


def get_console_handler(settings):
    c_handler = logging.StreamHandler()
    c_handler.setLevel(settings['logging_level'])
    c_handler.setFormatter(COLOR_LOGGING_FORMAT)
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
    nc_handler.setFormatter(COLOR_LOGGING_FORMAT)
    nc_handler.setLevel(settings['logging_level'])
    return nc_handler

def get_logging_handler(log_type, settings):
    try:
        if settings['enabled'] == 0:
            loggers_logger.debug('Logger {} is disabled.'.format(log_type))
            return None
        else:
            if log_type == 'console':
                return get_console_handler(settings)
            elif log_type == 'file':
                return get_file_handler(settings)
            elif log_type == 'netcat':
                return get_netcat_handler(settings)
            else:
                loggers_logger.error('Unknown logging handler {}'.format(log_type))
                return None
    except:
        return None

def get_handlers():
    logging_config = get_logging_config()
    handlers = []
    for log_type, settings in logging_config.items():
        log_handler = get_logging_handler(log_type, settings)
        if log_handler != None:
            handlers.append(log_handler)

    return tuple(handlers)        

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
        loggers_logger.error('Failed to initialise logging handler {}. Error: {}'.format(log_type, error))

    return logger

## Update Handlers code
def get_handler_index(logger, h_name):
    for h in logger.handlers:
        if h.name == h_name:
            return logger.handlers.index(h)
    return -1

def remove_handler(handlers, h_index):
    temp_handlers = list(handlers)
    temp_handlers.pop(h_index)
    return tuple(temp_handlers)

def add_handler(handlers, h_name, h_settings):
    h_name = h_name.split('_')[0]
    log_handler = get_logging_handler(h_name, h_settings)
    if log_handler != None:
        temp_handlers = list(handlers)
        temp_handlers.append(log_handler)
        return tuple(temp_handlers)

    return handlers

def update_handlers(logger):
    configuration = get_logging_config()
    #print(configuration.keys())

    # disable / enable handlers
    for h_config_name, h_config_settings in configuration.items():
    
        h_name = h_config_name + '_handler'

        # deleting handlers
        if h_config_settings['enabled'] == 0:
            h_index = get_handler_index(logger, h_name)
            if h_index != -1:
                logger.handlers = remove_handler(logger.handlers, h_index)
                loggers_logger.info('Handler {} was disabled'.format(h_name))

        if h_config_settings['enabled'] == 1:
            h_index = get_handler_index(logger, h_name)
            if h_index == -1:
                logger.handlers = add_handler(logger.handlers, h_name, h_config_settings)
                loggers_logger.info('Handler {} was enabled'.format(h_name))
    
        # change netcat handler configuration
        if h_name  == 'netcat_handler':
            h_index = get_handler_index(logger, h_name)
            if h_index != -1:
                for setting, value in h_config_settings.items():                    
                    if setting == 'enabled' or setting == 'logging_level':
                        continue
                    elif getattr(logger.handlers[h_index], setting) != value:
                        print(getattr(logger.handlers[h_index], setting))
                        loggers_logger.info('Update netcat configuration')
                        logger.handlers[h_index].update(h_config_settings['hostname'], h_config_settings['port']) 
    
# temp disabled
def update_logger(logger):
    handlers = logger.handlers
    new_config = logging_config = get_logging_config()
    for i in range(len(handlers)):
        h_name = handlers[i].name

        h_config = new_config[h_name.split('_')[0]]

        if h_name != 'netcat_handler':
            handlers[i].setLevel = new_config[h_name.split('_')[0]]['logging_level']
            loggers_logger.debug('Setting Handler: {} with new logging level: {}'.format(h_name, new_config[h_name.split('_')[0]]['logging_level']))
        else:

            new_hostname = new_config[h_name.split('_')[0]]['hostname']
            new_port = new_config[h_name.split('_')[0]]['port']
            new_logging_level = new_config[h_name.split('_')[0]]['logging_level']
            handlers[i].update(new_hostname, new_port, new_logging_level)
            loggers_logger.debug('Setting Handler: {} with new logging level: {}'.format(h_name, new_config[h_name.split('_')[0]]['logging_level']))
