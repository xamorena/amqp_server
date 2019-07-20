#!/usr/local/bin/python

import subprocess
import logging
import sys
import os
from urllib.parse import urlparse

LOG_FORMAT = '%(levelname)s @ %(asctime)s - %(name)s: %(message)s'
RABBITMQ_ADMIN = "./bin/rabbitmqadmin "
LOG_LEVEL = logging.INFO

def rabbitmq_admin(args, **kvargs):
    cmd = RABBITMQ_ADMIN + ' ' + args
    return subprocess.getstatusoutput(cmd)

def format_exchange(url, exchange, exchange_type, passive, durable, auto_delete, internal, arguments):
    return "-H {hn} -u {uid} -p {pwd} -V {vh} ".format(uid=url.username, pwd=url.password,hn=url.hostname,vh=url.path) + \
            ("declare exchange name={e} type={t} auto_delete={a} durable={d} internal={i}".format(e=exchange, t=exchange_type, a=auto_delete, d=durable, i=internal).lower())


def format_queue(url, queue, passive, exclusive, durable, auto_delete, arguments):
    return "-H {hn} -u {uid} -p {pwd} -V {vh} ".format(uid=url.username, pwd=url.password,hn=url.hostname,vh=url.path) + \
            "declare queue name={q} auto_delete={a} durable={d}".format(q=queue, a=auto_delete, d=durable).lower()


def format_queue_binding(url, queue, exchange, routing_key):
    return "-H {hn} -u {uid} -p {pwd} -V {vh} ".format(uid=url.username, pwd=url.password,hn=url.hostname,vh=url.path) + \
            "declare binding source={s} destination={d} destination_type=queue routing_key={r}".format(s=exchange, d=queue, r=routing_key).lower()

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
        logging.basicConfig(filename=args.logfile, level=LOG_LEVEL)
        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setLevel(LOG_LEVEL)
        log_formatter = logging.Formatter(LOG_FORMAT)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        from amqp_server import AmqpServerConfiguration
        config = AmqpServerConfiguration(filename=args.cfgfile)
        config.load_configuration()
        url = urlparse(config.settings['host'][0]['url'])    
        logger.info("RabbitMQ admin: {}".format(RABBITMQ_ADMIN))
        logger.info('Creating exchanges')
        for exchange in config.settings['exchanges']:
            req = format_exchange(url,
                                    exchange["name"],
                                    exchange_type=exchange["type"],
                                    passive=exchange["passive"],
                                    durable=exchange["durable"],
                                    auto_delete=exchange["auto_delete"],
                                    internal=exchange["internal"],
                                    arguments=exchange["arguments"])
            res = rabbitmq_admin(req)
            logger.info("## declare exchange\nrabbitmqadmin {}\n{}\n".format(req, res))

        logger.info('Creating queues')
        for queue in config.settings['queues']:
            req = format_queue(url,
                                queue["name"],
                                passive=queue["passive"],
                                exclusive=queue["exclusive"],
                                durable=queue["durable"],
                                auto_delete=queue["auto_delete"],
                                arguments=queue["arguments"])
            res = rabbitmq_admin(req)
            logger.info("## declare queue:\nrabbitmqadmin {}\n{}".format(req, res))

        logger.info('Creating bindings')
        for binding in config.settings['bindings']:
            if binding["destination_type"] == 'queue':
                req = format_queue_binding(url,
                                            binding["destination"],
                                            binding["source"],
                                            routing_key=binding["routing_key"])
                res = rabbitmq_admin(req)
                logger.info("## declare queue binding\nrabbitmqadmin {}\n{}".format(req, res))
    except Exception as err:
        logging.error("Error: {}".format(err))
    finally:
        logging.info('Bye!')


if __name__ == "__main__":
    main()
