from threading import Thread
import datetime
import Loggers
import logging
import time

import Alerts
import Tests

monitor_logger = Loggers.get_queue_logger(logging.DEBUG, __name__)

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
            testObj = Tests.Test_Factory()
            my_test = testObj.create_test(self.type, self)

            # running Test
            my_test.run(self)
        
            # creating Alert
            #  TODO check if the alert config changed before recreating test obj  
            #  TODO if the alert hasn't changed no need to instantiate Test class              


            # sending Alert if needed
            if self.alert_enabled == 1 and self.alert_type != 'n/a':
                try:
                    alertObj = Alerts.Alert_Factory()
                    alert = alertObj.create_alert(self.alert_type)

                    if self.failed >= self.ftt:
                        self.last_fail = datetime.datetime.now()
                        alert.fail(self)
                except Exception as er:
                    monitor_logger.exception('Failed to send alert. Error: {}, Object: {}'.format(er, self))
            else:
                monitor_logger.warn('Alert is disabled or not configured for monitor: {} / {}'.format(self.hostname, self.type))

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
