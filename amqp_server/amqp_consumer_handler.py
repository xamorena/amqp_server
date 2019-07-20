from .amqp_service_handler import AmqpServiceHandler
import logging
LOGGER = logging.getLogger(__name__)

class AmqpConsumerHandler(AmqpServiceHandler):

    def __init__(self, **kvargs):
        super(AmqpConsumerHandler, self).__init__(**kvargs)
        self.config = None

    def setup_handler(self, config):
        self.config = config

    def handle_message(self, channel, basic_deliver, properties, body):
        LOGGER.info("Message receive %s %s",
                    basic_deliver.delivery_tag, properties.app_id)
        channel.basic_ack(basic_deliver.delivery_tag)
