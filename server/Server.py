import sys
import shelve
from threading import Thread
import time
from queue import Queue
import logging
import builtins
import datetime
import os
from logging.handlers import  QueueListener


import Monitor


# local modulues
from Utils import Stats, Thread_manager, State_manager, load_monitors, load_alerts
from Alerts import Alert_Factory
from Tests import Test_Factory

import Loggers


# will use dirs later
curr_dir = os.getcwd()
CONFIG_FILE = os.path.join(curr_dir, 'config')

# load configuration
builtins.alerts = load_alerts()
builtins.monitors = load_monitors()

builtins.queue = Queue(1000)

# setting up main logger
main_logger = Loggers.get_queue_logger(logging.DEBUG, __name__)

# getting logging handlers configuration
handlers = Loggers.get_handlers()

# create queue listener
listener = QueueListener(log_queue, *handlers, respect_handler_level=True)

####### Main function starts here ########

# initiate Performance stats
try:
    server_stats = Stats(sys.argv[0], 30)
    server_stats.start()
except Exception as error:
    sys.exit('Failed to start Stats thread. Error: {}'.format(error))

# start monitors
try:
    # starting monitors
    threads = []
    for monitor in monitors:
        
        # create a thread
        current = Monitor.Monitor_test(monitor)

        # track threads
        threads.append(current)

        # start a thread
        current.start()
except Exception as error:
    sys.exit('Failed to start Monitor thread. Monitor ID: {}, Error: {}'.format(monitor['hostname'], error))

# start Thread manager
try:
    thread_manager = Thread_manager(CONFIG_FILE, threads)
    thread_manager.start()
except Exception as error:
    sys.exit('Failed to start Thread Mananger. Error: {}'.format(error))

# start State manager
try:
    state_manager = State_manager()
    state_manager.start()
except Exception as error:
    sys.exit('Failed to start State Mananger. Error: {}'.format(error))


main_logger.info('All processes started successfully')
listener.start()
while True:
    Loggers.update_handlers(listener)
    if not queue.empty():
        status, message = queue.get()
        if status:
            #logging.info(colored('{}'.format(message), 'green'))
            #logger.info(message)
            main_logger.info(colored('{}'.format(message), 'green'))
        else:
            #logging.info(colored('{}'.format(message), 'red'))
            #logger.info(message)
            main_logger.info(colored('{}'.format(message), 'red'))
    
    time.sleep(2)
listener.stop()

