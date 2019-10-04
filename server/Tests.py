import logging
from subprocess import check_output
import re
import requests
from termcolor import colored
import paramiko
import socket

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# disables Paramiko logging
logging.getLogger("paramiko").setLevel(logging.WARNING)

class Test:
    def __init__(self, config):
        self.hostname = config.hostname
        self.ftt = config.params['ftt']
        self.interval = config.params['interval']

class Ping_test(Test):

    def __init__(self, config):
        super().__init__(config)
        self.count = config.params['count']
        self.cmd = 'ping -c {} -t 2 {}'.format(self.count, self.hostname).split(' ')

    # function to get avg response time from the ping outpu
    @staticmethod
    def get_avg_time(response):
        agv_regex = re.compile(r'.*(\d{1,4}\.\d{3}\/(\d{1,4}\.\d{3})\/\d{1,4}\.\d{3}\/).*')
        avg_time = agv_regex.search(response)[2]
        return '{} ms'.format(round(float(avg_time), 2))

    def run(self,config):
        logging.debug('pinging %s' % self.hostname)


        # TODO - rework output
        try:
            response = check_output(self.cmd).decode('utf-8')
            config.result_info = 'Successful ping: {}, avg response time: {}'.format(self.hostname, Ping_test.get_avg_time(response))
            config.status = True
            config.failed = 0
        except Exception as e:
            config.result_info = 'Failed ping: {}. Error: {}'.format(self.hostname, e)  
            config.status = False       
            config.failed += 1



class Http_test(Test):
    def __init__(self, config):
        super().__init__(config)
        self.normalize_url(self.hostname)

        if 'allowed_codes' in config.params:
            self.allowed_codes = config.params['allowed_codes']
        else:
            self.allowed_codes = [200]

        if 'regexp' in config.params:
            self.regexp_text = config.params['regexp']
            self.regexp = re.compile(self.regexp_text)
        else:
            self.regexp = None

       

    def normalize_url(self, url):
        if not re.match(r'^https*\:\/\/', url):
            self.hostname = 'http://' + self.hostname 
    
    def run(self, monitor):

        try:
            if self.regexp == None: # no need to get page content if there is no regexp to look for
                request = requests.head(self.hostname)
            else:
                request = requests.get(self.hostname)
            
            if request.status_code not in self.allowed_codes:
                monitor.result_info = 'The HTTP response code {} for {} is not allowed'.format(request.status_code, self.hostname)
                monitor.status = False
                monitor.failed += 1
            else:
                if self.regexp == None:
                    monitor.result_info = 'Successful connection to {}. Status code {} is allowed.'.format(self.hostname, request.status_code)
                    monitor.status = True
                    monitor.failed = 0
                else:
                    matches = self.regexp.search(request.text, re.I)
                    
                    if matches:   
                        monitor.result_info = 'Successful connection to {}. Status code {} is allowed and regexp "{}" has a match'.format(self.hostname, request.status_code, self.regexp_text)
                        monitor.status = True
                        monitor.failed = 0
                    else:
                        monitor.result_info = 'Failed to find regexp {} on {}'.format(self.regexp_text, self.hostname)
                        monitor.status = False
                        monitor.failed += 1

        except requests.ConnectionError as er:
            monitor.result_info = 'Failed to connect to {}, error: {} '.format(self.hostname , er)
            monitor.failed +=1
            monitor.status = False


class Ssh_test(Test):
    def __init__(self, config):
        super().__init__(config)    
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.cmd = 'ls'
        self.timeout = 5
        self.username = config.params['username']
        self.password = config.params['password']      


    def run(self, monitor):
        try:
            self.client.connect(hostname=self.hostname, username=self.username, password=self.password)
            self.client.exec_command(self.cmd, self.timeout)
            self.client.close()
            monitor.result_info = 'Successful SSH connection to {}'.format(self.hostname)
            monitor.status = True
            monitor.failed = 0
        except Exception as er:
            monitor.result_info = 'Failed to connect with error: {}'.format(er)
            monitor.failed += 1
            monitor.status = False


class Tcp_test(Test):
    def __init__(self,config):
        super().__init__(config)
        self.port = config.params['port']
        self.timeout = config.params['timeout']
        self.conn_info = (self.hostname, self.port)

    
    def run(self, monitor):
        try:
            socket_conn = socket.create_connection(self.conn_info, timeout=self.timeout)
            socket_conn.close()
            monitor.result_info = 'Successful TCP connection to {}'.format(self.hostname)
            monitor.status = True
            monitor.failed = 0
        except Exception as er:
            monitor.result_info = 'Failed TCPto connect with error: {}'.format(er)
            monitor.failed += 1
            monitor.status = False


class Test_Factory():
   def create_test(self, typ, config):
        logging.debug('Generating {} test'.format(typ))
        target_class = typ.capitalize() + '_test'
        return globals()[target_class](config)
