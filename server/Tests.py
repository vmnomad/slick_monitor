import logging
from subprocess import check_output
import re
import requests
from termcolor import colored
import paramiko
import socket

from Utils import decrypt
#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

# disables Paramiko logging
logging.getLogger("paramiko").setLevel(logging.WARNING)

Tests_logger = logging.getLogger(__name__)
Tests_logger.setLevel(logging.INFO)
# set format
ch_format = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')

# create nc handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# set handler's format
ch.setFormatter(ch_format)

# set handler's level
ch.setLevel(logging.INFO)

Tests_logger.addHandler(ch)


class Test:
    def __init__(self, config):
        self.hostname = config.hostname
        self.ftt = config.ftt
        self.interval = config.interval
    
    @staticmethod
    def set_result(obj,typ, message):
        obj.result_info = message
        if typ == 'success':
            obj.status = True
            obj.failed = 0
        else:
            obj.status = False
            obj.failed += 1


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
            Ping_test.set_result(config, 'success', 'Successful ping: {}, avg response time: {}'.format(self.hostname, Ping_test.get_avg_time(response)))
        except Exception as e:
            Ping_test.set_result(config, 'fail', 'Failed ping: {}. Error: {}'.format(self.hostname, e))



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
                Ping_test.set_result(monitor, 'fail', 'The HTTP response code {} for {} is not allowed'.format(request.status_code, self.hostname))
            else:
                if self.regexp == None:
                    Ping_test.set_result(monitor, 'success', 'Successful connection to {}. Status code {} is allowed.'.format(self.hostname, request.status_code))
                else:
                    matches = self.regexp.search(request.text, re.I)
                    
                    if matches:   
                        Ping_test.set_result(monitor, 'success', 'Successful connection to {}. Status code {} is allowed and regexp "{}" has a match'.format(self.hostname, request.status_code, self.regexp_text))
                    else:
                        Ping_test.set_result(monitor, 'fail', 'Failed to find regexp {} on {}'.format(self.regexp_text, self.hostname))

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
        self.password = decrypt(config.params['password'])


    def run(self, monitor):
        try:
            self.client.connect(hostname=self.hostname, username=self.username, password=self.password)
            self.client.exec_command(self.cmd, self.timeout)
            self.client.close()
            Ping_test.set_result(monitor, 'success', 'Successful SSH connection to {}'.format(self.hostname))
        except Exception as er:
            Ping_test.set_result(monitor, 'fail', 'Failed SSH connection with error: {}'.format(er))


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
            Ping_test.set_result(monitor, 'success', 'Successful TCP connection to {}'.format(self.hostname))
        except Exception as er:
            Ping_test.set_result(monitor, 'fail', 'Failed TCP connection with error: {}'.format(er))




class Test_Factory():
   def create_test(self, typ, config):
        logging.debug('Generating {} test'.format(typ))
        target_class = typ.capitalize() + '_test'
        return globals()[target_class](config)