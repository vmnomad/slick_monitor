import subprocess
import re

avg_regex = re.compile(r'.*(\d{1,4}\.\d{3}\/(\d{1,4}\.\d{3})\/\d{1,4}\.\d{3}\/).*')
def get_avg_time(response):
    avg_time = avg_regex.search(response)[2]
    return '{} ms'.format(round(float(avg_time), 2))

cmd = 'ping -c 2 -t 2 google.com'.split(' ')
response = subprocess.check_output(cmd).decode('utf-8')
print(get_avg_time(response))



