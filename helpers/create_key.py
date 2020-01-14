from cryptography.fernet import Fernet
import os
import sys


def create_key():
    key = Fernet.generate_key()
    with open('monitor.key', 'w') as key_file:
        key_file.write(key.decode('utf-8'))


if not os.path.exists('monitor.key') or not os.path.isfile('monitor.key'):
    create_key()  



