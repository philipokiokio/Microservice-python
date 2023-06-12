import pika, json

params = pika.URLParameters(
    "amqps://xcrubsoc:xaCMqKTODLLL-BQVOBC9EZ87ji5V3i8e@rattlesnake.rmq.cloudamqp.com/xcrubsoc"
)

connection = pika.BlockingConnection(params)


channel = connection.channel()


def publish(method, body):
    property = pika.BasicProperties(method)
    channel.basic_publish(
        exchange="", routing_key="admin", body=json.dumps(body), properties=property
    )
