
import subprocess
from threading import Thread
import time
import datetime
import logging
from termcolor import colored
import shelve

from Tests import Test_Factory
from Alerts import Alert_Factory

COLOR = 'yellow'

#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

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
            raise

        output = output.stdout.decode('utf-8')
        output = output.strip(' ').split('\n')
        for line in output:
            if self.name in line:
                return line.strip(' ').split(' ')[0]
        raise 'Failed to find PID for program {}'.format(self.name)


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
            logging.info('CPU: {}, Mem: {}, Uptime: {}'.format(self.cpu(), self.memory(), self.uptime()))
            time.sleep(self.interval)

class Monitor_test(Thread):

    alertObj = Alert_Factory()

    def __init__(self, monitor_specs):
        Thread.__init__(self)
        self.id = monitor_specs['id']
        self.hostname = monitor_specs['hostname']
        self.type = monitor_specs['type']
        self.alert_type = monitor_specs['params']['alert_type'] 
        self.ftt = monitor_specs['params']['ftt']
        self.interval = monitor_specs['params']['interval']
        self.params = monitor_specs['params']
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
            if self.failed >= self.ftt:
                self.last_fail = datetime.datetime.now()
                self.alert.fail(self)

            test_result = [self.status, self.result_info]
            queue.put(test_result)

            # improved wait timer for quicker thread stop
            wait = 0
            while wait < self.interval:
                if self.alive == False:
                    break
                time.sleep(5)
                wait += 5
            #time.sleep(self.interval)

    def get_status(self):
        if self.status == True:
            return colored('Ping to {} was successful'.format(self.hostname), 'green')
        else:
            return colored('Ping to {} failed'.format(self.hostname), 'red')


class Thread_manager(Thread):
    def __init__(self, filename, threads, test_mode = False):
        Thread.__init__(self)
        self.daemon = True
        self.file_name = filename
        self.threads = threads
        self.test_mode = test_mode

    def run(self):
        id = 0
        while True:

            # get config file
            with shelve.open(self.file_name) as shelfFile:
                if self.test_mode == True:
                    # simulation of new monitors being added and removed
                    if id > 30:
                        thread_monitors = shelfFile['monitors1']
                    elif id > 15:
                        thread_monitors = shelfFile['monitors2']
                    else:
                        thread_monitors = shelfFile['monitors1']
                    shelfFile.close()
                else:
                    thread_monitors = shelfFile['monitors2']
                
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

            time.sleep(2)
            id += 1        