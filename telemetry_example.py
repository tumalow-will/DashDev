import os
import sys
import logging
import signal
import time
import yaml

from DashDev.mqtt_driver import Driver


logger = logging.getLogger(__name__)
#see log messages on the screen
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def load_config():
    '''
    load configs from config.yml in the top level folder
    '''
    HERE = os.path.split(os.path.realpath(__file__))[0]
    with open(os.path.join(HERE, 'config.yml')) as f:
        config = yaml.load(f)
        print config
    return config

config = load_config()
host=config['host']
token=config['token']

device = Driver(host=host, token=token)

def quit(*args, **kwargs):
    print('Exiting')
    device.tearDown()
    sys.exit(0)

#quit the demo when ctrl+c is hit
signal.signal(signal.SIGINT, quit)

print('Publishing forever.  Ctrl+C to quit')
counter = 0
delay = 5
while 1:
    data={'mydata': counter}
    device.telemetry(data=data)
    counter+=1
    time.sleep(delay)
