
import subprocess
from threading import Thread
import threading
import time
import datetime
import logging
from termcolor import colored
import shelve
import os
import json
from cryptography.fernet import Fernet
import sqlite3
import ast
import sys
import os
import Loggers

import Monitor



# Database Name
db_folder = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
db_name = 'slick_monitor_db.sqlite3'
DB_PATH = os.path.join(db_folder, db_name)

# Color for Stats logging
COLOR = 'yellow'

# setting up module logger
utils_logger = Loggers.get_queue_logger(logging.DEBUG, __name__)

# Monitor paramers that are allowed to be updated
MUTABLE_PARAMS = ['interval', 'ftt', 'alert_type', 'alert_enabled', 'params']

def load_alerts():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * from ALERTS")
        result = cursor.fetchall()

        alerts = {}
        for alert in result:
            alerts[alert['type']] =json.loads(alert['settings'])
        return alerts
    except Exception as error:
        utils_logger.error('Failed to load alerts configuration. Error: {}'.format(error))

def get_key():
    key = os.getenv('MONITOR_KEY')
    return key

# takes key as byte literal and secret as string
def encrypt(secret):
    key = get_key()
    secret = secret.encode('utf-8')

    cipher_suite = Fernet(key)
    ciphered_text = cipher_suite.encrypt(secret)

    # returns byte literal
    return ciphered_text.decode('utf-8')

# takes key as byte literal and secret as string
def decrypt(secret):
    key = get_key()
    secret = secret.encode('utf-8')
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(secret)
    return decrypted_text.decode('utf-8') 


def load_monitors():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * from MONITORS")
        result = cursor.fetchall()
        
        # convert Row to Dict to be able to update dict parameters
        monitors = [dict(row) for row in result]

        for i in range(len(monitors)):
            monitors[i]['params'] = json.loads(monitors[i]['params'])
        conn.close()
        
        return monitors
    except Exception as error:
        sys.exit('Failed to load monitors. Error: {}'.format(error))

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
            utils_logger.error('failed to capture PID of {}, Error: {}'.format(self.name, er))

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
            utils_logger.info('Total Threads: {}, Monitors: {}, CPU: {}, Mem: {}, Uptime: {}'.format(threading.active_count(), len(monitor_threads), self.cpu(), self.memory(), self.uptime()))
            time.sleep(self.interval)

# responsible for start/stop of threads and updating the threads parameteres
class Thread_manager(Thread):


    def __init__(self, filename, threads):
        Thread.__init__(self)
        self.daemon = True
        self.file_name = filename
        self.threads = threads


    @staticmethod
    def update_params(threads, monitors):
        for i in range(len(threads)):
            # get monitor config with the same ID as thread
            temp_monitor = [monitor for monitor in monitors if monitor['id'] == threads[i].id][0]
            
            # compare all parameters from the list
            for my_param in MUTABLE_PARAMS:

                # convert to dict if comparing params
                if my_param == 'params':
                    if temp_monitor[my_param] != getattr(threads[i], my_param):
                        utils_logger.info(colored('Updating PARAMS for {}, type: {}. Old Params: {}, New Params: {}'.format(threads[i].hostname, threads[i].type, getattr(threads[i], my_param), temp_monitor[my_param]), 'blue'))
                        threads[i].params = temp_monitor[my_param]
                else:
                    if temp_monitor[my_param] != getattr(threads[i], my_param):                       
                        utils_logger.info(colored('Updating {} for {}, type: {}. Old setting: {}, New setting: {}'.format(my_param.upper(), threads[i].hostname, threads[i].type, getattr(threads[i], my_param), temp_monitor[my_param]), 'blue'))
                        setattr(threads[i], my_param, temp_monitor[my_param])

    def run(self):
        while True:

            thread_monitors = load_monitors()
                
            # get IDs of running threads
            thread_ids = [obj.id for obj in self.threads]
            
            # loop through monitors are added
            for monitor in thread_monitors:

                # check if it is started
                if not monitor['id'] in thread_ids:
                    utils_logger.info(colored('Starting new thread for {}'.format(monitor['hostname']), 'red'))
                    new_thread = Monitor.Monitor_test(monitor)
                    self.threads.append(new_thread)
                    new_thread.start()

            # get list of configured monitor ids
            monitor_ids = [monitor['id'] for monitor in thread_monitors]

            for obj in self.threads:
                if not obj.id in monitor_ids:
                    utils_logger.info(colored('Stopping thread for {}'.format(obj.hostname), 'red'))
                    obj.alive = False
                    obj.join()
                    self.threads.remove(obj)     

            # update params
            Thread_manager.update_params(self.threads, thread_monitors)

            time.sleep(1)    

# updates States table
class State_manager(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
    
    def run(self):
        errors = 0
        while True:
            try:
                # open DB connection
                conn = sqlite3.connect(DB_PATH)

                # reset STATES table
                conn.execute('DELETE FROM STATES')
                conn.commit()
                utils_logger.debug('Cleaned States Table')
                # populate table with new values
                monitor_threads = [thread for thread in threading.enumerate() if hasattr(thread, 'id')]
                
                for thread in monitor_threads:
                    state = thread.get_status()
                    conn.execute('INSERT INTO STATES (monitor_id, state) VALUES ({}, {})'.format(thread.id, state))


                conn.commit()
                utils_logger.debug('Updated States Table')
                conn.close()
            except Exception as er:
                errors += 1
                utils_logger.info(colored('Failed to update States table. Error: {}, Total Errors: {}'.format(er, errors), 'red'))
            finally:
                conn.close()

            time.sleep(1)