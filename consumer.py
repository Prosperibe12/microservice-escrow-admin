import pika
from decouple import config

params = pika.URLParameters(config('AMPQ_URL'))
connection  = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='app')

def callback(ch, method, propeties, body):
    print("Received here")
    print("Body", body)

channel.basic_consume(queue='app', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
channel.close()