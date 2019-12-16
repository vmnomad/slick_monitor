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
class Monitor_test(Thread):

    #alertObj = Alert_Factory()
    def __init__(self, monitor_specs):
        Thread.__init__(self)
        self.id = monitor_specs['id']
        self.hostname = monitor_specs['hostname']
        self.type = monitor_specs['type']
        self.alert_type = monitor_specs['alert_type']
        self.alert_enabled = monitor_specs['alert_enabled']
        self.ftt = monitor_specs['ftt']
        self.interval = monitor_specs['interval']
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
            alert = alertObj.create_alert(self.alert_type)

            # sending Alert if needed
            if self.alert_enabled == 1:
                try:
                    if self.failed >= self.ftt:
                        self.last_fail = datetime.datetime.now()
                        alert.fail(self)
                except Exception as er:
                    main_logger.exception('Failed to send alert. Error: {}, Object: {}'.format(er, self))
            else:
                main_logger.info('Alert is disabled for monitor: {} / {}'.format(self.hostname, self.type))

            # passing result data to queue
            test_result = [self.status, self.result_info]
            #queue.put(test_result)

            # improved wait timer for quicker thread stop
            wait = 0
            while wait < self.interval:
                if self.alive == False:
                    break
                time.sleep(1)
                wait += 1

    def get_status(self):
        if self.status == True:
            #return colored('Ping to {} was successful'.format(self.hostname), 'green')
            return 1
        else:
            #return colored('Ping to {} failed'.format(self.hostname), 'red')
            return 0

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

