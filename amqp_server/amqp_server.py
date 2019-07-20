from .amqp_server_config import AmqpServerConfiguration
from .amqp_service_component import AmqpServiceComponent
import json
import pika
import random
import functools
from urllib.parse import urlparse
from importlib import import_module

from pika.adapters.asyncio_connection import AsyncioConnection

import logging
LOGGER = logging.getLogger(__name__)


class AmqpServer(object):

    def __init__(self, config=AmqpServerConfiguration(), **kwargs):
        super(AmqpServer, self).__init__(**kwargs)
        self.config = config if config != None else AmqpServerConfiguration()
        self.handlers = dict()
        self.components = []
        self.setup_services()

    def setup_service_handler(self, name, config):
        try:
            klass_name = config['class']
            LOGGER.info('Registering service handler: %s', klass_name)
            module_path, class_name = klass_name.rsplit('.', 1)
            module = import_module(module_path)
            klass = getattr(module, class_name)
            handler = klass()
            handler.setup_handler(config)
            self.handlers[name] = handler
            LOGGER.info('Service handler registered: %s', klass_name)
        except Exception as err:
            LOGGER.error('Handler registration failed: %s', str(err))
            pass

    def setup_service_component(self, config):
        try:
            LOGGER.info('Registrating service component')
            c = AmqpServiceComponent(self)
            handler = self.handlers[config['handler']]
            c.setup_component(config, handler)
            self.components.append(c)
            LOGGER.info('Service component registered')
        except Exception as err:
            LOGGER.error('Handler registration failed: %s', str(err))
            pass

    def setup_services(self):
        try:
            LOGGER.info('Configuring services')
            self.config.load_configuration()
            for name in self.config.settings['handlers']:
                self.setup_service_handler(name,  self.config.settings['handlers'][name])
            for component in self.config.settings['components']:
                self.setup_service_component(component)
            LOGGER.info('Services configured')
        except Exception as err:
            LOGGER.error('Service configuration failed: %s', str(err))
            pass

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
            LOGGER.warning('Connection close failed')

    def open_connection(self):
        LOGGER.info('Configuring connection')
        params = []
        for entry in self.config.settings['host']:
            url = urlparse(entry['url'])
            creds = pika.PlainCredentials(url.username, url.password)
            param = pika.ConnectionParameters(
                host=url.hostname,
                port=url.port,
                virtual_host=url.path,
                credentials=creds
            )
            params.append(param)
            LOGGER.info('AMQP host urls configured')
        try:
            self.connection = self.create_connection(params[0])
            self.connection.ioloop.run_forever()
        except:
            LOGGER.warning('Connection open failed')
        finally:
            return self.connection

    def open_channel(self):
        LOGGER.info('Creating a new channel')
        self.channel = self.connection.channel(
            on_open_callback=self.on_channel_opened)
        return self.channel

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
        for component in self.components:
            component.start(self.channel)
