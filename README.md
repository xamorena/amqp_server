# AMQP Server Utility (amqp_server)

## rabbitmqadmin

```bash
wget http://${RABBITMQ_HOST}:15672/cli/rabbitmqadmin
```

### Display

```bash
  list connections
  list channels
  list consumers
  list exchanges
  list queues
  list bindings
  list users
  list vhosts
  list permissions
  list nodes
  list parameters
  list policies
  list operator_policies
  list vhost_limits
  show overview
```

### Object Manipulation

```bash
  declare exchange name type [auto_delete durable internal arguments]
  declare queue name [auto_delete durable arguments node]
  declare binding source destination [destination_type routing_key arguments]
  declare vhost name [tracing]
  declare user name password OR password_hash tags [hashing_algorithm]
  declare permission vhost user configure write read
  declare parameter component name value
  declare policy name pattern definition [priority apply-to]
  declare operator_policy name pattern definition [priority apply-to]
  declare vhost_limit vhost name value
  delete exchange name
  delete queue name
  delete binding source destination_type destination properties_key
  delete vhost name
  delete user name
  delete permission vhost user
  delete parameter component name
  delete policy name
  delete operator_policy name
  delete vhost_limit vhost name
  close connection name
  purge queue name
```

### Broker Definitions

```bash
  export file
  import file
```

### Publishing and Consuming

```bash
  publish routing_key [payload properties exchange payload_encoding]
  get queue [count ackmode payload_file encoding]
```
