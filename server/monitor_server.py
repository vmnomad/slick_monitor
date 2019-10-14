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
from Utils import Stats, Monitor_test, Thread_manager, State_manager
# build config
os.system('python build_config.py')

curr_dir = os.getcwd()
CONFIG_FILE = os.path.join(curr_dir, 'config')


# config
shelfFile = shelve.open(CONFIG_FILE)
builtins.global_config = shelfFile['global_config']
builtins.monitors = Thread_manager.read_config()
builtins.queue = Queue(1000)
shelfFile.close()


logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# main function starts here

# initiate Performance stats
server_stats = Stats(sys.argv[0], 30)
server_stats.start()


threads = []
# start initial config
for monitor in monitors:
    
    # create a thread, add fake id
    current = Monitor_test(monitor)

    # track threads
    threads.append(current)

    # start a thread
    current.start()


# start thread manager
thread_manager = Thread_manager(CONFIG_FILE, threads)
thread_manager.start()

state_manager = State_manager()
state_manager.start()


while True:
    if not queue.empty():
        status, message = queue.get()
        if status:
            logging.info(colored('{}'.format(message), 'green'))
        else:
            logging.info(colored('{}'.format(message), 'red'))
    time.sleep(0.1)


