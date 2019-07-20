import pika 
import json
import logging

LOGGER = logging.getLogger(__name__)

class AmqpServiceComponent(object):

    def __init__(self, server, **kwargs):
        super(AmqpServiceComponent, self).__init__(**kwargs)
        self.server = server
        self.config = None
        self.mode = None
        self.handler = None
        self.channel = None

    def setup_component(self, config, handler):
        self.config = config
        self.mode = config['mode'].upper()
        self.handler = handler

    def start(self, channel):
        if self.mode == "RPC":
            self.start_rpcproxy(channel)
        elif self.mode == "PUB":
            self.start_publisher(channel)
        elif self.mode == "SUB":
            self.start_subscriber(channel)
         
    def start_rpcproxy(self, channel):
        queue = self.config['queue_name']
        self.channel = channel
        self.consumer_tag = self.channel.basic_consume(queue, self.handler.handle_message)

    def start_publisher(self, channel):
        properties = pika.BasicProperties(app_id=self.config['id'],
                                          content_type=self.config['message']['type'],
                                          headers={})
        exchange = self.config['exchange_name']
        routing_key = self.config['routing_key']
        message = self.config['message']['data']
        self.channel = channel
        self.channel.basic_publish(exchange,
                                   routing_key,
                                   json.dumps(message, ensure_ascii=False),
                                   properties)

    def start_subscriber(self, channel):
        queue = self.config['queue_name']
        self.channel = channel
        self.consumer_tag = self.channel.basic_consume(queue, self.handler.handle_message)
