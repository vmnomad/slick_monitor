
import subprocess
from threading import Thread
import time
import datetime
import logging
from termcolor import colored

COLOR = 'yellow'

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

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


