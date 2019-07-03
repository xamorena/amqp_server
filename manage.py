import subprocess
import logging
import sys

LOG_FORMAT = '%(levelname)s @ %(asctime)s - %(name)s: %(message)s'
RABBITMQADMIN = './bin/rabbitmqadmin -H localhost '


def rabbitmqadmin(args, **kvargs):
    cmd = RABBITMQADMIN + args
    return subprocess.getstatusoutput(cmd)


def setup_exchange(exchange, exchange_type, passive, durable, auto_delete, internal, arguments):
    return rabbitmqadmin(
        "declare exchange name={e} type={t} auto_delete={a} durable={d} internal={i}".format(
            e=exchange, t=exchange_type, a=auto_delete, d=durable, i=internal).lower())


def setup_queue(queue, passive, exclusive, durable, auto_delete, arguments):
    return rabbitmqadmin(
        "declare queue name={q} auto_delete={a} durable={d}".format(
            q=queue, a=auto_delete, d=durable).lower())


def setup_queue_binding(queue, exchange, routing_key):
    return rabbitmqadmin(
        "declare binding source={s} destination={d} destination_type=queue routing_key={r}".format(
            s=exchange, d=queue, r=routing_key).lower())


def main():
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--cfgfile", type=str,
                            default="etc/config.json", help="configuration file")
        parser.add_argument("-l", "--logfile", type=str,
                            default="logs/amqp_server.log", help="logging file")
        parser.add_argument("-v", "--verbose",
                            action="store_true", help="display information")
        args = parser.parse_args()
        logging.basicConfig(filename=args.logfile, level=logging.INFO)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setLevel(logging.INFO)
        log_formatter = logging.Formatter(LOG_FORMAT)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        from amqp_server import AmqpServerConfiguration
        config = AmqpServerConfiguration(filename=args.cfgfile)
        config.load_configuration()
        logger.info('Creating exchanges')
        for exchange in config.settings['exchanges']:
            logger.info("declare exchange {}".format(setup_exchange(exchange["name"],
                                                                    exchange_type=exchange["type"],
                                                                    passive=exchange["passive"],
                                                                    durable=exchange["durable"],
                                                                    auto_delete=exchange["auto_delete"],
                                                                    internal=exchange["internal"],
                                                                    arguments=exchange["arguments"])))

        logger.info('Creating queues')
        for queue in config.settings['queues']:
            logger.info("declare queue {}".format(setup_queue(queue["name"],
                                                              passive=queue["passive"],
                                                              exclusive=queue["exclusive"],
                                                              durable=queue["durable"],
                                                              auto_delete=queue["auto_delete"],
                                                              arguments=queue["arguments"])))

        logger.info('Creating bindings')
        for binding in config.settings['bindings']:
            if binding["destination_type"] == 'queue':
                logger.info("declare binding {}".format(setup_queue_binding(binding["destination"],
                                                                            binding["source"],
                                                                            routing_key=binding["routing_key"])))
    except Exception as err:
        logging.error("Error: {}".format(err))
    finally:
        logging.info('Bye!')


if __name__ == "__main__":
    main()
