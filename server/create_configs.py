import pprint
import shelve

global_config = {
    'email' :
    {
        'smtp_host' : 'smtp.gmail.com',
        'smtp_port' : 587,
        'from_addr' : 'slick.monitor.35@google.com',
        'to_addr' : 'akopbayev@vmware.com',
        'ssl' : True,
        'username' : 'slick.monitor.35',
        'password' : 'VMware1!',
        'alert_interval' : 300
    },
    'syslog' : 
    {
        None
    }
}

monitors = [
    {
        'hostname' : 'google.com',
        'type' : 'ping',
        'params' : {
            'interval' : 15,
            'ftt' : 3,
            'alert_type' : 'email',
            'count' : 3
        }
    },
    {
        'hostname' : '4.4.4.4',
        'type' : 'ping',
        'params' : {
            'interval' : 15,
            'ftt' : 3,
            'alert_type' : 'email',
            'count' : 3
        }
    },
    {
        'hostname' : 'https://www.vmware.com',
        'type' : 'http',
        'params' : {
            'interval' : 10,
            'ftt' : 1,
            'alert_type' : 'email'
        }
    },
    {
        'hostname' : 'bbc.com',
        'type' : 'http',
        'params' : {
            'interval' : 10,
            'ftt' : 3,
            'alert_type' : 'email',
        }
    }
]


monitors1 = [
    {
        'hostname' : '1.1.1.1',
        'type' : 'ping',
        'params' : {
            'interval' : 5,
            'ftt' : 3,
            'alert_type' : 'email',
            'count' : 3
        }
    }
]

with open('configs.py', 'w') as config_file:
    config_file.write('global_config = ' + pprint.pformat(global_config) + '\n')
    config_file.write('monitors = ' + pprint.pformat(monitors) + '\n')
