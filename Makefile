RABBITMQ_HOST="localhost"

amqp_admin_cli_update: ./bin/rabbitmqadmin

./bin/rabbitmqadmin:
	cd ./bin && wget http://${RABBITMQ_HOST}:15672/cli/rabbitmqadmin && cd ../

amqp_declaration: 
	python3 manage.py

.PHONY: amqp_declaration
