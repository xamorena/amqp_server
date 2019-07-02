import sys
import logging

def main():
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--url", type=str, default="amqp://guest:guest@localhost:5672/%2F", help="AMQP server url" )
        args = parser.parse_args()
        from amqp.server.amqp_publisher import AmqpPublisher
        publisher = AmqpPublisher(args.url)
        publisher.run()
    except Exception as err:
        logging.info("Error: {}".format(err))

if __name__ == "__main__":
    main()
