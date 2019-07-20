import abc

class AmqpServiceHandler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def setup_handler(self, config):
        pass

    @abc.abstractmethod
    def handle_message(self, channel, basic_deliver, properties, body):
        pass
