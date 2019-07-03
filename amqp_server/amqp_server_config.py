import json
import logging

LOGGER = logging.getLogger(__name__)


class AmqpServerConfiguration:

    DEFAULT_CONFIG_FILE = "etc/config.json"

    def __init__(self, filename=None):
        self.filename = filename if filename != None else self.DEFAULT_CONFIG_FILE
        self.settings = None
        #self.load_configuration()

    def load_configuration(self):
        try:
            with open(self.filename, "r") as cfgfile:
                LOGGER.info("loading configuration")  
                self.settings = json.load(cfgfile)
                LOGGER.info("configuration loaded")  
        except Exception as err:
            LOGGER.error("load configuration failed: {e}".format(e=err))
