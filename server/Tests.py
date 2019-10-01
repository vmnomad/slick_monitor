import configs
import pprint
import logging
from subprocess import check_output
import re
import requests
from termcolor import colored

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
# get configuration
#monitors_config = configs.monitors


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
            #config.result_info = Ping_test.get_avg_time(response)
            #logging.debug('Successful ping: {}, avg response time: {}'.format(self.hostname, config.result_info))
            config.status = True
            config.failed = 0
        except Exception as e:
            config.status = False
            config.result_info = e
            logging.debug("Error: {}".format(e))                
            config.failed += 1
            return False




class Http_test(Test):
    def __init__(self, config):
        super().__init__(config)
        self.normalize_url(self.hostname)

    def normalize_url(self, url):
        if not re.match(r'^https*\:\/\/', url):
            self.hostname = 'http://' + self.hostname 
    
    def run(self, monitor):
        
        try:
            request = requests.head(self.hostname)
            monitor.failed = 0
            if request.status_code == 200:
                #logging.debug('Successful connection to {}'.format(self.hostname))
                monitor.result_info = 'Successful connection to {}'.format(self.hostname)
                monitor.status = True
            else:
                monitor.result_info = 'Partially successful connection to {} with status code {}'.format(self.hostname, request.status_code)
                monitor.status = False

        except requests.ConnectionError as er:
            monitor.result_info = 'Failed to connect to {}, error: {} '.format(self.hostname , er)
            monitor.failed +=1


class SSH_test:
    pass


class Test_Factory():
   def create_test(self, typ, config):
        logging.debug('Generating {} test'.format(typ))
        target_class = typ.capitalize() + '_test'
        #if typ == 'ping': return Ping_test()
        #if typ == 'http': return Http_test()
        return globals()[target_class](config)



