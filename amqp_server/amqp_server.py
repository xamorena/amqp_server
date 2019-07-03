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
        self.config.load_configuration()

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
        try:
            LOGGER.info('Stopping server')
            self.close_connection()
        except:
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

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        LOGGER.info("Message receive %s %s",
                    basic_deliver.delivery_tag, properties.app_id)
        # forward to the handler
        self.channel.basic_ack(basic_deliver.delivery_tag)

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
        LOGGER.info("AMQP RPCProxy Component ID: %s", component['id'])
        queue = component['queue_name']
        self.consumer_tag = self.channel.basic_consume(queue, self.on_message)

    def start_pub_component(self, component):
        LOGGER.info("AMQP Publisher Component ID: %s", component['id'])
        headers = {u'X-AUTH-ID': u'ABCD123456789'}
        properties = pika.BasicProperties(app_id=component['id'],
                                          content_type=component['message']['type'],
                                          headers=headers)
        exchange = component['exchange_name']
        routing_key = component['routing_key']
        message = component['message']['data']
        self.channel.basic_publish(exchange,
                                   routing_key,
                                   json.dumps(message, ensure_ascii=False),
                                   properties)

    def start_sub_component(self, component):
        LOGGER.info("AMQP Subscriber Component ID: %s", component['id'])
        queue = component['queue_name']
        self.consumer_tag = self.channel.basic_consume(queue, self.on_message)

    def start_components(self):
        LOGGER.info('Creating exchanges')
        for exchange in self.config.settings['exchanges']:
            self.channel.exchange_declare(exchange["name"],
                                          exchange_type=exchange["type"],
                                          passive=exchange["passive"],
                                          durable=exchange["durable"],
                                          auto_delete=exchange["auto_delete"],
                                          internal=exchange["internal"],
                                          arguments=exchange["arguments"])

        LOGGER.info('Creating queues')
        for queue in self.config.settings['queues']:
            self.channel.queue_declare(queue["name"],
                                       passive=queue["passive"],
                                       exclusive=queue["exclusive"],
                                       durable=queue["durable"],
                                       auto_delete=queue["auto_delete"],
                                       arguments=queue["arguments"])

        LOGGER.info('Creating bindings')
        for binding in self.config.settings['bindings']:
            if binding["destination_type"] == 'queue':
                self.channel.queue_bind(binding["destination"],
                                        binding["source"],
                                        routing_key=binding["routing_key"])

        self.channel.basic_qos(prefetch_count=1)
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
