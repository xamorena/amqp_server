import logging
import sys

def main():
    server = None
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--cfgfile", type=str, default="etc/config.json", help="configuration file" )
        parser.add_argument("-l", "--logfile", type=str, default="logs/amqp_server.log", help="logging file" )
        parser.add_argument("-v", "--verbose", action="store_true", help="display information")
        args = parser.parse_args()
        logging.basicConfig(filename=args.logfile, level=logging.INFO)
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s @ %(asctime)s - %(name)s: %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
        from amqp.server import AmqpServer
        from amqp.server import AmqpServerConfiguration
        server = AmqpServer(config=AmqpServerConfiguration(filename=args.cfgfile))
        print("AMQP Server: amqp_server release 1.0 is running on {}".format("localhost"))
        server.start()
    except Exception as err:
        logging.error("Error: {}".format(err))
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    main()
