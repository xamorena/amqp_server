FROM rabbitmq:3-management
LABEL name=mqbroker:1.0.0 version=1.0.0
LABEL maintainer="xavier.amorena@labri.fr"
ENV RABBITMQ_DEFAULT_USER guest
ENV RABBITMQ_DEFAULT_PASS guest
EXPOSE 1883
EXPOSE 5672
EXPOSE 15672
RUN rabbitmq-plugins enable --offline rabbitmq_management rabbitmq_federation_management rabbitmq_stomp
