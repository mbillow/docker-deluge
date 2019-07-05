#!/usr/bin/python

'''Ping PIA API every minute to get port'''

import string
import random
from time import sleep
import requests
import logging
from os import system

logging.basicConfig(level=logging.INFO)

# Generate Client Key for API Use
def gen_client_key():
    # Mimick: head -n 100 /dev/urandom | sha256sum | tr -d ' -')
    pool = string.letters + string.digits
    return ''.join(random.choice(pool) for i in xrange(64))


def get_port(client_key):
    response = requests.get(
        'http://209.222.18.222:2000/?client_id={}'.format(client_key),
        timeout=3)
    return response.json()['port']

def get_deluge_pass():
    auth = file('/config/auth', 'r').readline()
    password = auth.split(":")[1]
    logging.info('Local User Password: {}'.format(password))
    return password

def set_deluge_port(password, port):
    # Make sure the daemon has actually started
    sleep(5)
    logging.info("Setting Deluge Port to {}".format(port))
    command = "deluge-console 'connect 127.0.0.1:58846 localclient" +\
        " {password}; config --set listen_ports ({port}, {port})'".format(
            password=password,
            port=port)
    system(command)


if __name__ == "__main__":
    current_key = gen_client_key()
    logging.info("Using Client Key: {}".format(current_key))
    while True:
        # Default timeout between calls: 10s
        wait = 10
        try:
            port = get_port(current_key)
            password = get_deluge_pass()
            set_deluge_port(password, port)
            # Create longer timeout in the case of success.
            wait=600
        except requests.exceptions.ConnectionError:
            logging.info(
                'Connection Error: Either disconnected or already have port.')
        except requests.exceptions.Timeout:
            logging.info(
                'Connection Timout: Server took longer than 3 seconds to respond.')
        sleep(wait)

