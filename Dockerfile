FROM rabbitmq:3-management
LABEL name=mbroker:3.0.0 version=3.0.0
LABEL maintainer="xavier.amorena@labri.fr"

ENV RABBITMQ_DEFAULT_USER admin
ENV RABBITMQ_DEFAULT_PASS admin
ENV PLUGIN_VERSION=0.10.0
ENV AUTOCLUSTER_TYPE=consul
ENV AUTOCLUSTER_CLEANUP=true
ENV CLEANUP_WARN_ONLY=false
ENV RABBITMQ_ERLANG_COOKIE=VOLBRAIN20AMQP09D201906
ENV RABBITMQ_DEFAULT_VHOST=/
# ENV CONSUL_HOST=consul
# ENV CONSUL_PORT=8500
# ENV CONSUL_SVC=mbroker
# ENV CONSUL_SVC_ADDR_AUTO=true

EXPOSE 1883
EXPOSE 5672
EXPOSE 15672

RUN apt-get update && \
    apt-get install -y wget

RUN cd /opt/rabbitmq/plugins && \
    wget -q https://github.com/rabbitmq/rabbitmq-autocluster/releases/download/${PLUGIN_VERSION}/autocluster-${PLUGIN_VERSION}.ez && \
    wget -q https://github.com/rabbitmq/rabbitmq-autocluster/releases/download/${PLUGIN_VERSION}/rabbitmq_aws-${PLUGIN_VERSION}.ez

VOLUME [ "/var/lib/rabbitmq" ]

RUN rabbitmq-plugins --offline enable \
    rabbitmq_management \
    rabbitmq_consistent_hash_exchange \
    rabbitmq_federation \
    rabbitmq_federation_management \
    rabbitmq_mqtt \
    rabbitmq_shovel \
    rabbitmq_shovel_management \
    rabbitmq_stomp \
    rabbitmq_web_stomp \
    autocluster
