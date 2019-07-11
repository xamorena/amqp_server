import logging
import sys

LOG_FORMAT = '%(levelname)s @ %(asctime)s - %(name)s: %(message)s'
LOG_LEVEL = logging.DEBUG

def main():
    server = None
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--cfgfile", type=str, default="etc/config.json", help="configuration file" )
        parser.add_argument("-l", "--logfile", type=str, default="logs/amqp_server.log", help="logging file" )
        parser.add_argument("-v", "--verbose", action="store_true", help="display information")
        args = parser.parse_args()
        logging.basicConfig(filename=args.logfile, level=LOG_LEVEL)
        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setLevel(LOG_LEVEL)
        log_formatter = logging.Formatter(LOG_FORMAT)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        from amqp_server import AmqpServer
        from amqp_server import AmqpServerConfiguration
        server = AmqpServer(config=AmqpServerConfiguration(filename=args.cfgfile))
        logger.info("AMQP Server: amqp_server release 1.0 is running on %s", "localhost")
        server.start()
    except Exception as err:
        logging.error("Error: %s", str(err))
    except KeyboardInterrupt:
        server.stop()
    finally:
        logging.info('Bye!')

if __name__ == "__main__":
    main()
