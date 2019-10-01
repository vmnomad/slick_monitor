from threading import Thread
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
import configs
# config
monitors_config = configs.monitors
global_config = configs.global_config




# main function starts here

#logging.debug(colored('Starting program {}'.format(sys.argv[0]), 'red'))

q = Queue(100)

class monitor_test(Thread):
    def __init__(self, monitor_specs):
        Thread.__init__(self)
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


    def __str__(self):
        return '{} test for {}'.format(self.type.capitalize(), self.hostname)
    

    def run(self):
        while True:
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


#threads = []
# TODO add monitoring of threads and restart if needed

# TODO add shutting down threads if monitor is removed from the config
for monitor in monitors_config:
    
    # get config

    # create a thread
    current = monitor_test(monitor)
    
    # track threads
    
    #threads.append(current)

    # start a thread
    current.start()


# getting memory stats
def Memory():
    stats_obj = stats.Stats(sys.argv[0])
    while True:
        logging.info(colored('Current Memory Usage: {}'.format(stats_obj.memory()), 'blue'))
        time.sleep(10)

thread_obj = Thread(target=Memory)
thread_obj.daemon = True
thread_obj.start()

while True:
    if not q.empty():
        status, message = q.get()
        if status:
            logging.info(colored('{}'.format(message), 'green'))
        else:
            logging.info(colored('{}'.format(message), 'red'))
    time.sleep(2)


    
