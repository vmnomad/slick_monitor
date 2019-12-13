from cryptography.fernet import Fernet
import os


def get_key():
    key = os.getenv('MONITOR_KEY')
    return key


def encrypt(secret):
    key = get_key()
    secret = secret.encode('utf-8')

    cipher_suite = Fernet(key)
    ciphered_text = cipher_suite.encrypt(secret)

    # returns byte literal
    return ciphered_text.decode('utf-8')


def decrypt(secret):
    key = get_key()
    secret = secret.encode('utf-8')
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(secret)
    return decrypted_text.decode('utf-8') 