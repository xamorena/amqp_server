import abc

class AmqpServiceHandler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def handle_message(self, message):
        pass

    @abc.abstractmethod
    def setup_handler(self, config):
        pass
