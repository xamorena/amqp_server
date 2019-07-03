import sys
import logging

LOG_FORMAT = '%(levelname)s @ %(asctime)s - %(name)s: %(message)s'

def main():
    client = None
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--url", type=str, default="amqp://guest:guest@localhost:5672/%2F", help="AMQP server url" )
        parser.add_argument("-e", "--exchange", type=str, default="task_exchange", help="AMQP exchange name" )
        parser.add_argument("-t", "--exchange-type", type=str, default="topic", help="AMQP exchange type" )
        parser.add_argument("-q", "--queue", type=str, default="task_queue", help="AMQP queue n me" )
        parser.add_argument("-r", "--routing-key", type=str, default="task", help="AMQP routing key" )
        parser.add_argument("-l", "--logfile", type=str, default="logs/amqp_client.log", help="logging file" )
        args = parser.parse_args()
        logging.basicConfig(filename=args.logfile, level=logging.INFO)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setLevel(logging.INFO)
        log_formatter = logging.Formatter(LOG_FORMAT)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        from amqp_server.amqp_publisher import AmqpPublisher
        client = AmqpPublisher(args.url, args.exchange, args.exchange_type, args.queue, args.routing_key)
        client.run()
    except Exception as err:
        logging.info("Error: {}".format(err))
    except KeyboardInterrupt:
        client.close()
        logging.info('Bye!')

if __name__ == "__main__":
    main()
