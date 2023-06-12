import pika, json
from main import Product, SessionLocal

db = SessionLocal()

params = pika.URLParameters(
    "amqps://xcrubsoc:xaCMqKTODLLL-BQVOBC9EZ87ji5V3i8e@rattlesnake.rmq.cloudamqp.com/xcrubsoc"
)

connection = pika.BlockingConnection(params)


channel = connection.channel()
channel.queue_declare("main")


def callback(ch, method, properties, body):
    print("recieved in main")
    data = json.loads(body)
    print(data)

    if properties.content_type == "product_created":
        product = Product(id=data["id"], title=data["title"])
        db.add(product)
        db.commit()
    elif properties.content_type == "product_updated":
        product = db.query(Product).filter(id == data["id"]).first()
        if product:
            for key, value in data.items():
                setattr(product, key, value)
            db.commit()

    elif properties.content_type == "product_deleted":
        product = db.query(Product).filter(id == data).first()
        if product:
            db.delete(product)
            db.commit()
    pass


channel.basic_consume("main", callback, auto_ack=True)


print("started consuming")

channel.start_consuming()


channel.close()
