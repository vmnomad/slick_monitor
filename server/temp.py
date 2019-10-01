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
        'id' : 0,
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
        'id' : 1,
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
        'id' : 2,
        'hostname' : 'https://www.vmware.com',
        'type' : 'http',
        'params' : {
            'interval' : 10,
            'ftt' : 1,
            'alert_type' : 'email'
        }
    },
    {
        'id' : 3,
        'hostname' : 'bbc.com',
        'type' : 'http',
        'params' : {
            'interval' : 10,
            'ftt' : 3,
            'alert_type' : 'email',
        }
    }
]


shelfFile = shelve.open('config.txt')
shelfFile['monitors1'] = monitors1
shelfFile['monitors2'] = monitors2
shelfFile['global_config'] = global_config
shelfFile.close()



shelfFile = shelve.open('config.txt')
print(shelfFile['global_config'])
#print(list(shelfFile.values()))
shelfFile.close()