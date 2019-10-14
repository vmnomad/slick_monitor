
import subprocess
from threading import Thread
import threading
import time
import datetime
import logging
from termcolor import colored
import shelve
import os

from Tests import Test_Factory
from Alerts import Alert_Factory

# Color for Stats logging
COLOR = 'yellow'

# Monitor paramers that are allowed to be updated
MUTABLE_PARAMS = ['interval', 'ftt', 'alert_type', 'alert_enabled', 'params']


import sqlite3
import ast


class Stats(Thread):
    def __init__(self, name, interval):
        Thread.__init__(self)
        self.daemon = True
        self.name = name
        self.pid = self.find_pid()
        self.interval = interval
        self.memory_usage = ''
        self.cpu_usage = ''
        self.start_time = datetime.datetime.now()

    def find_pid(self):
        try:
            output = subprocess.run(['ps'], stdout = subprocess.PIPE)
        except Exception as er:
            print('failed to capture PID of', self.name, ', Error:', er)

        output = output.stdout.decode('utf-8')
        output = output.strip(' ').split('\n')
        for line in output:
            if self.name in line:
                return line.strip(' ').split(' ')[0]
        raise Exception('Failed to find PID for program {}'.format(self.name))


    # some black magic shit with passing cmd output between pipes in cli
    def memory(self):
        
        # first part of the command
        cli1 = subprocess.Popen(['ps', 'u', '-p', self.pid], stdout=subprocess.PIPE)
        
        # second part of the command
        c2_arg = '{sum=sum+$6}; END {print sum/1024}'
        c2 = ['awk', c2_arg]
        cli2 = subprocess.Popen(c2, stdin=cli1.stdout, stdout=subprocess.PIPE)

        # Allow cli1 to receive a SIGPIPE if cli2 exits.
        cli1.stdout.close()
        output,err = cli2.communicate()

        if err == None:
            # decode result
            memory = output.decode('utf-8').split('\n')[0]
            memory = round(float(memory), 2)
            return str(memory) + ' MB'
        else:
            return 'Error: ' + err

    def cpu(self):
        cpu_cli = 'ps -p {} -o %cpu'.format(self.pid).split(' ')
        cpu_usage = subprocess.check_output(cpu_cli).decode('utf-8').strip().split()[1]
        return str(cpu_usage.strip(' ')) + '%'

    def uptime(self):
        current_time = datetime.datetime.now()
        uptime = current_time - self.start_time
        days = uptime.days
        hours, seconds = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return '{} days, {} hours, {} minutes, {} seconds'.format(colored(days, COLOR), colored(hours, COLOR), colored(minutes, COLOR), colored(seconds, COLOR))



    def run(self):
        while True:
            monitor_threads = [thread for thread in threading.enumerate() if hasattr(thread, 'id')]
            logging.info('Total Threads: {}, Monitors: {}, CPU: {}, Mem: {}, Uptime: {}'.format(threading.active_count(), len(monitor_threads), self.cpu(), self.memory(), self.uptime()))
            time.sleep(self.interval)

class Monitor_test(Thread):

    alertObj = Alert_Factory()

    def __init__(self, monitor_specs):
        Thread.__init__(self)
        self.id = monitor_specs['id']
        self.hostname = monitor_specs['hostname']
        self.type = monitor_specs['type']
        self.alert_type = monitor_specs['alert_type']
        self.alert_enabled = monitor_specs['alert_enabled']
        self.ftt = monitor_specs['ftt']
        self.interval = monitor_specs['interval']
        self.params = dict(monitor_specs['params'])
        self.alert = Monitor_test.alertObj.create_alert(self.alert_type, global_config)

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
            #alertObj = Alert_Factory()
            #alert = alertObj.create_alert(self.alert_type, global_config)

            # sending Alert if needed
            if self.alert_enabled == 1:
                try:
                    if self.failed >= self.ftt:
                        self.last_fail = datetime.datetime.now()
                        self.alert.fail(self)
                except Exception as er:
                    print('Failed to send alert. Error: {}, Object: {}'.format(er, self))
            else:
                logging.info('Alert is disabled for monitor: {} / {}'.format(self.hostname, self.type))

            # passing result data to queue
            test_result = [self.status, self.result_info]
            queue.put(test_result)

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


# responsible for start/stop of threads and updating the threads parameteres
class Thread_manager(Thread):
    def __init__(self, filename, threads):
        Thread.__init__(self)
        self.daemon = True
        self.file_name = filename
        self.threads = threads

    @staticmethod
    def read_config():
        conn = sqlite3.connect('server.db', timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * from MONITORS")
        result = cursor.fetchall()
        
        # convert Row to Dict to be able to update dict parameters
        monitors = [dict(row) for row in result]

        for i in range(len(monitors)):
            temp_dict = ast.literal_eval(monitors[i]['params'])
            monitors[i]['params'] = tuple([(k, v) for k,v in temp_dict.items()])
        #raise Exception('error')
        conn.close()
        #logging.debug('Successfully read monitors configuration from MONITORS table')
        return monitors

    @staticmethod
    def update_params(threads, monitors):
        for thread in threads:
            # get monitor config with the same ID as thread
            temp_monitor = [monitor for monitor in monitors if monitor['id'] == thread.id][0]
            
            # compare all parameters from the list
            for my_param in MUTABLE_PARAMS:

                # convert to dict if comparing params
                if my_param == 'params':
                    if dict(temp_monitor[my_param]) != getattr(thread, my_param):
                        print(colored('param {} is different'.format(my_param), 'red'))
                        logging.info(colored('Updating monitor parameters for {}, type: {}'.format(thread.hostname, thread.type), 'blue'))
                        thread.params = dict(temp_monitor[my_param])
                else:
                    if temp_monitor[my_param] != getattr(thread, my_param):
                        print(colored('param {} is different'.format(my_param), 'red'))
                        setattr(thread, my_param, temp_monitor[my_param])

    def run(self):
        while True:

            thread_monitors = Thread_manager.read_config()
                
            # get IDs of running threads
            thread_ids = [obj.id for obj in self.threads]
            
            # loop through monitors are added
            for monitor in thread_monitors:

                # check if it is started
                if not monitor['id'] in thread_ids:
                    logging.info(colored('Starting new thread for {}'.format(monitor['hostname']), 'red'))
                    new_thread = Monitor_test(monitor)
                    self.threads.append(new_thread)
                    new_thread.start()

            # get list of configured monitor ids
            monitor_ids = [monitor['id'] for monitor in thread_monitors]

            for obj in self.threads:
                if not obj.id in monitor_ids:
                    logging.info(colored('Stopping thread for {}'.format(obj.hostname), 'red'))
                    obj.alive = False
                    obj.join()
                    self.threads.remove(obj)     

            # compare params
            Thread_manager.update_params(self.threads, thread_monitors)


            time.sleep(1)    


class State_manager(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
    
    def run(self):
        errors = 0
        while True:
            try:
                # open DB connection
                conn = sqlite3.connect('server.db')
                conn.commit()
                logging.debug('Cleaned States Table')

                # reset STATES table
                conn.execute('DELETE FROM STATES')

                # populate table with new values
                monitor_threads = [thread for thread in threading.enumerate() if hasattr(thread, 'id')]
                
                for thread in monitor_threads:
                    #print("ID: {}, Status: {}".format(thread.id, thread.status))
                    state = thread.get_status()
                    conn.execute('INSERT INTO STATES (monitor_id, state) VALUES ({}, {})'.format(thread.id, state))


                conn.commit()
                logging.debug('Updated States Table')
                conn.close()
            except Exception as er:
                errors += 1
                logging.info(colored('Failed to update States table. Error: {}, Total Errors: {}'.format(er, errors), 'red'))
            finally:
                conn.close()

            time.sleep(1)