from threading import Thread
import threading
import time
from termcolor import colored
from subprocess import check_output
from queue import Queue
import logging

import datetime

from Tests import Test_Factory
from alerts import Alert_Factory

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

import stats
import sys


import shelve

# config
shelfFile = shelve.open('config.txt')
global_config = shelfFile['global_config']
monitors = shelfFile['monitors1']
shelfFile.close()




# main function starts here

#logging.debug(colored('Starting program {}'.format(sys.argv[0]), 'red'))

q = Queue(100)

class monitor_test(Thread):
    def __init__(self, monitor_specs):
        Thread.__init__(self)
        self.id = monitor_specs['id']
        self.hostname = monitor_specs['hostname']
        self.type = monitor_specs['type']
        self.alert_type = monitor_specs['params']['alert_type'] 
        self.ftt = monitor_specs['params']['ftt']
        self.interval = monitor_specs['params']['interval']
        self.params = monitor_specs['params']

        # generic params 
        self.failed = 0
        self.daemon = True
        self.alert_time = datetime.datetime.now() - datetime.timedelta(days=1)
        self.last_fail = 0
        self.status = False
        self.result_info = ''
        self.alive = True


    def __str__(self):
        return '{} test for {}'.format(self.type.capitalize(), self.hostname)
    

    def run(self):
        while self.alive:
            # creating Test
            # TODO check if the test config changed before recreating test obj
            # TODO if the config hasn't changed no need to instantiate Test class
            testObj = Test_Factory()
            my_test = testObj.create_test(self.type, self)

            # running Test
            my_test.run(self)
        
            # creating Alert
            #  TODO check if the alert config changed before recreating test obj  
            #  TODO if the alert hasn't changed no need to instantiate Test class              
            alertObj = Alert_Factory()
            alert = alertObj.create_alert(self.alert_type, global_config)

            # sending Alert if needed
            if self.failed >= self.ftt:
                self.last_fail = datetime.datetime.now()
                alert.fail(self)

            test_result = [self.status, self.result_info]
            q.put(test_result)

            time.sleep(self.interval)

    def get_status(self):
        if self.status == True:
            return colored('Ping to {} was successful'.format(self.hostname), 'green')
        else:
            return colored('Ping to {} failed'.format(self.hostname), 'red')


threads = []

# build


# TODO add monitoring of threads and restart if needed

# TODO add shutting down threads if monitor is removed from the config

for monitor in monitors:
    
    # get config

    # create a thread, add fake id
    current = monitor_test(monitor)


    # track threads
    threads.append(current)

    # start a thread
    current.start()




def manage_threads():
    id = 0
    
    while True:
        shelfFile = shelve.open('config.txt')
        if id > 10:
            monitors = shelfFile['monitors1']
        elif id > 5:
            monitors = shelfFile['monitors2']
        else:
            monitors = shelfFile['monitors1']
        shelfFile.close()

        print('Number of current monitors', len(monitors))
        thread_ids = [obj.id for obj in threads]
        print('Number of current threads:', len(thread_ids))
        for monitor in monitors:

            # check if it is started
            if not monitor['id'] in thread_ids:
                print(colored('Starting new thread for {}'.format(monitor['hostname']), 'red'))
                new_thread = monitor_test(monitor)
                threads.append(new_thread)
                new_thread.start()

        # get list of configured monitor ids
        monitor_ids = [monitor['id'] for monitor in monitors]

        for obj in threads:
            if not obj.id in monitor_ids:
                print(colored('Stopping thread for {}'.format(obj.hostname), 'red'))
                obj.alive = False
                obj.join()
                threads.remove(obj)     

        time.sleep(2)
        id += 1

thread_manager = Thread(target=manage_threads)
thread_manager.daemon = True
thread_manager.start()


# getting memory stats
def Memory():
    stats_obj = stats.Stats(sys.argv[0])
    while True:
        logging.info(colored('Current Memory Usage: {}'.format(stats_obj.memory()), 'blue'))
        time.sleep(10)

thread_obj = Thread(target=Memory)
thread_obj.daemon = True
thread_obj.start()






sleep_timer = 0
while True:
    if not q.empty():
        status, message = q.get()
        if status:
            logging.info(colored('{}'.format(message), 'green'))
        else:
            logging.info(colored('{}'.format(message), 'red'))
    #print('number of threads: {}'.format(len(threading.enumerate())))

    #if sleep_timer > 15:        
    #    threads[0].alive = False
    #    print('id: ', threads[0].id)
    #    print(colored('Stopping thread', 'red'))
    #    threads[0].join()
    
    #sleep_timer += 2
    time.sleep(2)


