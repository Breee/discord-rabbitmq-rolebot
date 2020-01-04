from discord.ext import commands
from time import sleep
import pika
import config as config
import json
from utility.globals import LOGGER
from threading import Thread
from collections import namedtuple

RoleAssignment = namedtuple('RoleAssignment', ['guild_id', 'role_id', 'give_role', 'take_role'])

class RabbitMQManager(object):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        LOGGER.info(f'Connecting to {config.RABBITMQ_HOST} on port {config.RABBITMQ_PORT}')
        self.sender_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT,
                                          credentials=pika.PlainCredentials(config.RABBITMQ_USERNAME,
                                                                            config.RABBITMQ_PASSWORD)))
        self.consumer_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT,
                                          credentials=pika.PlainCredentials(config.RABBITMQ_USERNAME,
                                                                            config.RABBITMQ_PASSWORD)))
        self.sender_channel = self.sender_connection.channel()
        self.consumer_channel = self.consumer_connection.channel()
        self.consumer_thread = None
        self.messages = []

    def declare_sender_queue(self, queue_name):
        self.sender_channel.queue_declare(queue=queue_name)
        LOGGER.info(f'Declared queue {queue_name} for sender')

    def declare_consumer_queue(self, queue_name):
        self.consumer_channel.queue_declare(queue=queue_name)
        LOGGER.info(f'Declared queue {queue_name} for consumer')

    def send_message(self, routing_key, body):
        self.sender_channel.basic_publish(exchange='', routing_key=routing_key, body=body)
        LOGGER.info(f'Sent Message: {body} to {routing_key}')

    def handle_pogobackend_message(self, ch, method, properties, body):
        LOGGER.info(f'Received {json.loads(body)}')
        message = json.loads(body)
        guild_to_roles = message['guild_to_roles']
        role_assignments = message['role_assignments']
        for entry in guild_to_roles:
            self.messages.append(RoleAssignment(guild_id=entry['guild_id'],
                                                role_id=entry['role_id'],
                                                give_role=role_assignments['give_role'],
                                                take_role=role_assignments['take_role'])
                                 )

    def define_consumer(self, queue, callback_function):
        self.consumer_channel.basic_consume(queue=queue, on_message_callback=callback_function, auto_ack=True)

    def start_consumer(self):
        self.consumer_thread = Thread(target=self.consumer_channel.start_consuming)
        self.consumer_thread.start()

    def disconnect(self):
        self.sender_connection.close()
        self.consumer_connection.close()

    def fetch_messages(self):
        messages = self.messages.copy()
        self.messages = []
        return messages

if __name__ == '__main__':
    mgr = RabbitMQManager(bot=None)
    queue = 'pogobackend_queue'
    mgr.define_consumer(queue, mgr.handle_pogobackend_message)
    mgr.declare_sender_queue(queue)
    mgr.declare_consumer_queue(queue)
    mgr.start_consumer()
    while mgr.consumer_thread.isAlive():
        sleep(2)
        mgr.send_message(routing_key=queue, body=json.dumps({"give_role": [1, 2, 3, 4], "take_role": [5, 6, 7]}))
