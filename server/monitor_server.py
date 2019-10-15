import sys
import shelve
from threading import Thread
import time
from termcolor import colored
from subprocess import check_output
from queue import Queue
import logging
import builtins
import datetime
import os

# local modulues
from Utils import Stats, Monitor_test, Thread_manager, State_manager, load_monitors
from Alerts import load_alerts
# will use dirs later
curr_dir = os.getcwd()
CONFIG_FILE = os.path.join(curr_dir, 'config')


# load configuration
builtins.alerts = load_alerts()
builtins.monitors = load_monitors()


builtins.queue = Queue(1000)

# setting up logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')



####### Main function starts here ########


# initiate Performance stats
try:
    server_stats = Stats(sys.argv[0], 30)
    server_stats.start()
except Exception as error:
    sys.exit('Failed to start Stats thread. Error: {}'.format(error))

try:
    # starting monitors
    threads = []
    for monitor in monitors:
        
        # create a thread
        current = Monitor_test(monitor)

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


logging.info('All processes started successfully')

while True:
    if not queue.empty():
        status, message = queue.get()
        if status:
            logging.info(colored('{}'.format(message), 'green'))
        else:
            logging.info(colored('{}'.format(message), 'red'))
    time.sleep(0.1)


