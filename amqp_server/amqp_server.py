from .amqp_server_config import AmqpServerConfiguration

import json
import pika
import random
import logging
import functools

from pika.adapters.asyncio_connection import AsyncioConnection

LOGGER = logging.getLogger(__name__)

class AmqpServer(object):

    def __init__(self, config=AmqpServerConfiguration(), **kvargs):
        super(AmqpServer, self).__init__(**kvargs)
        self.config = config if config != None else AmqpServerConfiguration()

    def start(self):
        LOGGER.info('Starting server')
        self.open_connection()
        LOGGER.info('Server started')

    def restart(self):
        LOGGER.info('Restarting server')
        self.close_connection()
        self.open_connection()
        LOGGER.info('Server restarted')

    def stop(self):
        LOGGER.info('Stopping server')
        self.close_connection()
        LOGGER.info('Server stopped')

    def on_connection_opened(self, _unused_connection):
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_channel_closed(self, channel, reason):
        LOGGER.info('Channel closed')

    def on_channel_opened(self, channel):
        LOGGER.info('Channel opened')
        self.channel = channel
        self.channel.add_on_close_callback(self.on_channel_closed)
        self.start_components()

    def on_connection_open_error(self, _unused_connection, err):
        LOGGER.info('Connection open failed, reconnect')
        self.restart()

    def on_connection_closed(self, _unused_connection, reason):
        LOGGER.info('Connection closed')

    def on_exchange_declareok(self, component):
        LOGGER.info('Exchange declare ok')

    def on_queue_declareok(self, component):
        LOGGER.info('Queue declare ok')

    def on_queue_bindok(self, component):
        LOGGER.info('Queue bind ok')

    def on_message(self, object, _unused_channel, basic_deliver, properties, body):
        LOGGER.info('Message receive')

    def create_connection(self, parameters):
        LOGGER.info('Creating a new connection')
        return AsyncioConnection(parameters=parameters,
                                 on_open_callback=self.on_connection_opened,
                                 on_open_error_callback=self.on_connection_open_error,
                                 on_close_callback=self.on_connection_closed)

    def close_connection(self):
        LOGGER.info('Closing connection')
        try:
            self.connection.ioloop.stop()
            self.connection.close()
            self.connection = None
        except:
            LOGGER.warnning('Connection close failed')

    def open_connection(self):
        LOGGER.info('Configuring connection')
        params = []
        for entry in self.config.settings['urls']:
            param = pika.URLParameters(entry['url'])
            params.append(param)
            LOGGER.info('AMQP host urls configured')
        try:
            parameters = params[0]
            self.connection = self.create_connection(parameters)
            self.connection.ioloop.run_forever()
        except:
            LOGGER.warnning('Connection open failed')
        finally:
            return self.connection

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self.channel = self.connection.channel(
            on_open_callback=self.on_channel_opened)
        return self.channel

    def start_rpc_component(self, component):
        LOGGER.info("Starting AMQP RPC Component ID: {}".format(component['id']))
        ename = component['exchange']['name']
        etype = component['exchange']['type']
        rkey = component['exchange']['routing_key']
        qname = component['queue']['name']
        passive = component['exchange']['passive']
        durable = component['exchange']['durable']
        auto_delete = component['exchange']['auto_delete']
        internal = component['exchange']['internal']
        self.channel.exchange_declare(exchange=ename, exchange_type=etype, passive=passive, durable=durable, auto_delete=auto_delete, internal=internal)
        passive = component['queue']['passive']
        durable = component['queue']['durable']
        exclusive = component['queue']['exclusive']
        auto_delete = component['queue']['auto_delete']
        self.channel.queue_declare(queue=qname)
        self.channel.queue_bind(qname, ename, routing_key=rkey)
        self.channel.basic_qos(prefetch_count=1)
        auto_ack = component['queue']['auto_ack']
        exclusive = component['queue']['exclusive']
        cb = functools.partial(self.on_message, object=component)
        self.consumer_tag = self.channel.basic_consume(qname,
                                                       cb, auto_ack=auto_ack,
                                                       exclusive=exclusive)

    def start_pub_component(self, component):
        LOGGER.info("Starting AMQP Publisher Component ID: {}".format(component['id']))
        ename = component['exchange']['name']
        etype = component['exchange']['type']
        rkey = component['exchange']['routing_key']
        qname = component['queue']['name']
        #cbe = functools.partial(self.on_exchange_declareok, component=component)
        self.channel.exchange_declare(exchange=ename, exchange_type=etype)#, callback=cbe)
        #cbq = functools.partial(self.on_queue_declareok, component=component)
        self.channel.queue_declare(queue=qname)#, callback=cbq)
        #cbb = functools.partial(self.on_queue_bindok, component=component)
        self.channel.queue_bind(qname, ename, routing_key=rkey)#, callback=cbb)
        self.channel.basic_qos(prefetch_count=1)
        headers = {u'X-AUTH-ID': u'ABCD123456789'}
        properties = pika.BasicProperties(app_id=component['id'],
                                          content_type=component['message']['type'],
                                          headers=headers)
        message = component['message']['data']
        self.channel.basic_publish(ename, rkey, json.dumps(
            message, ensure_ascii=False), properties)

    def start_sub_component(self, component):
        LOGGER.info("Starting AMQP Subscriber component ID: {}".format(component['id']))
        qname = component['queue']['name']
        #cbq = functools.partial(self.on_queue_declareok, component=component)
        self.channel.queue_declare(queue=qname)#, callback=cbq)
        self.channel.basic_qos(prefetch_count=1)
        auto_ack = component['queue']['auto_ack']
        exclusive = component['queue']['exclusive']
        cb = functools.partial(self.on_message, object=component)
        self.consumer_tag = self.channel.basic_consume(qname, 
                                                       cb, 
                                                       auto_ack=auto_ack,
                                                       exclusive=exclusive)

    def start_components(self):
        LOGGER.info('Starting components')
        for component in self.config.settings['components']:
            mode = component['mode'].upper()
            if mode == "RPC":
                self.start_rpc_component(component)
            elif mode == "PUB":
                self.start_pub_component(component)
            elif mode == "SUB":
                self.start_sub_component(component)
            else:
                LOGGER.warning('Unsupported component mode {}'.format(mode))
