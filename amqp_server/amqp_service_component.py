
class AmqpServiceComponent(object):

    def __init__(self, server, **kwargs):
        super(AmqpServiceComponent, self).__init__(**kwargs)
        self.server = server
        self.config = None

    def setup_component(self, config):
        self.config = config
