import pika
import config as config

connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_HOST, credentials=pika.PlainCredentials('rabbit', 'rabbit')))
channel = connection.channel()

channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(
    queue='hello', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()