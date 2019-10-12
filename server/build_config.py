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
    },
    'slack' : 
    {
        'webhook' : 'https://hooks.slack.com/services/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',
        'alert_interval' : 300
    }
}


shelfFile = shelve.open('config')
#shelfFile['monitors1'] = monitors1
#shelfFile['monitors2'] = monitors2
shelfFile['global_config'] = global_config
shelfFile.close()