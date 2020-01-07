# used the script from this blog https://www.alexkras.com/how-to-restart-python-script-after-exception-and-run-it-forever/
# to restart the monitoring server on exception

#!/usr/bin/python
from subprocess import Popen
import sys

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = Popen("python " + filename, shell=True)
    p.wait()