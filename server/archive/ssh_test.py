import paramiko

USER = 'vmnomad'
PASSWORD = 'TTkJmjSudbgK8w'
HOST = 'tty.sdf.org1'


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#stdin, stdout, stderr = client.exec_command('ls')


class Ssh_test(Test):
    def __init__(self, config):
        super().__init__(config)    
        self.client = paramiko.SSHClient()
        self.cmd = 'ls'
        self.timeout = 5
        self.username = config.params['username']
        self.password = config.params['password']      


    def run(self):
        try:
            self.client.connect(hostname=self.hostname, username=self.username, password=self.password)
            client.exec_command(self.cmd, self.timeout)
            client.close()
        except Exception as er:
            print('Failed to connect with error:', er)


#transport = client.get_transport()
#transport.send_ignore()