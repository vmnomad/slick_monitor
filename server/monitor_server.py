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


# local modulues

from Utils import Stats, Monitor_test, Thread_manager



CONFIG_FILE = 'config'
test_mode = True

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# config
shelfFile = shelve.open(CONFIG_FILE)
builtins.global_config = shelfFile['global_config']
builtins.monitors = shelfFile['monitors2']
builtins.queue = Queue(100)
shelfFile.close()


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
thread_manager = Thread_manager(CONFIG_FILE, threads, test_mode)
thread_manager.start()

while True:
    if not queue.empty():
        status, message = queue.get()
        if status:
            logging.info(colored('{}'.format(message), 'green'))
        else:
            logging.info(colored('{}'.format(message), 'red'))
    time.sleep(2)


