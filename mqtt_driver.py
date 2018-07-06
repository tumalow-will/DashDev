import json
import logging
import traceback
logger = logging.getLogger(__name__)

import paho.mqtt.client as mqtt


class Topics(object):
    def __init__(self):
        self.attributes = 'v1/devices/me/attributes'
        self.rpc = 'v1/devices/me/rpc'
        self.telemetry = 'v1/devices/me/telemetry'

    def get_message_id(self, message):
        return message.topic.split('/')[-1]

TOPICS = Topics()

class Driver(object):
    '''
    Wrapper around MQTT client that provides some helpful rails for working
    with Tumalow servers.
    '''
    def __init__(self, host, token):
        self.token = token

        self.client = mqtt.Client("device_client")
        
        #attach our callback functions to the client
        self.client.on_connect = self.on_connect 
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message        
        self.client.on_subscribe = self.on_subscribe

        #set the credentials and connect
        self.client.username_pw_set(self.token)
        self.client.connect(host)
        self.client.loop_start()

        self.callbacks = {'connect': [], 
                        'publish': [], 
                        'message': []
                        }

        self.rpc_method_handlers = {}

    def on_connect(self, client, userdata, flags, rc):
        '''
        When the client connects, subscribe to the appropriate topics
        Result codes:
        https://jaimyn.com.au/mqtt-connection-failed-status-codes-connack-return-codes/
        '''
        logger.info("result code: " + str(rc))

        client.subscribe(TOPICS.attributes)
        client.subscribe(TOPICS.attributes+'/response/+')
        client.subscribe(TOPICS.rpc+'/request/+')

    def on_publish(self, client, userdata, mid):
        '''
        Fires when our client publishes data back upstream
        '''
        logger.info('published', extra={'mid': str(mid)})

    def on_subscribe(self, client, userdata, mid, granted_qos):
        '''
        Fires when our client subscribes to a topic.  
        '''
        pass

    def on_message(self, client1, userdata, message):
        '''
        Fires when we receive a message
        '''
        request_id = TOPICS.get_message_id(message)
        payload = json.loads(message.payload)
        logger.info("message received", extra={'payload': payload})

        try:
            resp = self.handle_rpc(payload)
        except Exception as err:
            error_text = traceback.format_exc()
            logger.error(error_text)
            resp = error_text

        #publish the response to /response/ topic
        client1.publish(TOPICS.rpc+'/response/{0}'.format(request_id),
                json.dumps(resp))

        for func in self.callbacks['message']:
            func({'payload': payload, 'resp': resp})

    def handle_rpc(self, payload):
        method = payload['method']
        params = payload['params']

        func = self.rpc_method_handlers.get(method, None)
        if func is not None:
            return func(params)

    def add_rpc_handler(self, method, func):
        self.rpc_method_handlers[method] = func

    def register_callback(self, message_type, func):
        '''
        message_type is one of 'connect', 'publish', or 'message'
        '''
        assert message_type in self.callbacks.keys()

        self.callbacks[message_type].append(func)

    def telemetry(self, data):
        return self.client.publish(TOPICS.telemetry, json.dumps(data) )

    def tearDown(self):
        self.client.disconnect()


