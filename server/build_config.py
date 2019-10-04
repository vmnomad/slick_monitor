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

monitors1 = [
    {
        'id' : 0,
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

monitors2 = [
    {
        'id' : 1,
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
        'id' : 2,
        'hostname' : '4.4.4.4',
        'type' : 'ping',
        'params' : {
            'interval' : 3,
            'ftt' : 3,
            'alert_type' : 'email',
            'count' : 3
        }
    },
    {
        'id' : 3,
        'hostname' : 'https://www.vmware.com',
        'type' : 'http',
        'params' : {
            'interval' : 10,
            'ftt' : 1,
            'alert_type' : 'email',
            'allowed_codes' : [200, 201]
        }
    },
    {
        'id' : 4,
        'hostname' : 'bbc.com',
        'type' : 'http',
        'params' : {
            'interval' : 10,
            'ftt' : 3,
            'alert_type' : 'email',
            'allowed_codes' : [200, 201]
        }
    },
    {
        'id' : 5,
        'hostname' : 'tty.sdf.org',
        'type' : 'ssh',
        'params' : {
            'username' : 'vmnomad',
            'password' : 'TTkJmjSudbgK8w',
            'interval' : 10,
            'ftt' : 3,
            'alert_type' : 'email'
        }
    },
    {
        'id' : 6,
        'hostname' : 'optus.com.au',
        'type' : 'tcp',
        'params' : {
            'port' : 443,
            'interval' : 10,
            'ftt' : 3,
            'alert_type' : 'email',
            'timeout' : 2
        }
    }
]


shelfFile = shelve.open('config')
shelfFile['monitors1'] = monitors1
shelfFile['monitors2'] = monitors2
shelfFile['global_config'] = global_config
shelfFile.close()