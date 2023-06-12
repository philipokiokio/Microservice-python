import pika, json, django, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin.settings")
django.setup()
from product.models import Product

params = pika.URLParameters(
    "amqps://xcrubsoc:xaCMqKTODLLL-BQVOBC9EZ87ji5V3i8e@rattlesnake.rmq.cloudamqp.com/xcrubsoc"
)

connection = pika.BlockingConnection(params)


channel = connection.channel()
channel.queue_declare("admin")


def callback(ch, method, properties, body):
    print("recieved in terminal")
    data = json.loads(body)
    print(data)
    if properties.content_type == "product_liked":
        product = Product.objects.filter(id=data["id"]).first()
        if product:
            product.likes += 1
            product.save()
        print("product_liked")
    pass


channel.basic_consume("admin", callback, auto_ack=True)


print("started consuming")

channel.start_consuming()


channel.close()
