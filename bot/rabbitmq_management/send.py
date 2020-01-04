from time import sleep

import pika
import config as config
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(config.RABBITMQ_HOST, credentials=pika.PlainCredentials('rabbit', 'rabbit')))
channel = connection.channel()

channel.queue_declare(queue='pogobackend_queue')
message = {
    "guild_to_roles" : [{"guild_id": 409418083632152577, "role_id": 616562233475989514}],
    "role_assignments":
        {
            "give_role":  [377196211054051339],
            "take_role": []
        }
    }
channel.basic_publish(exchange='', routing_key=config.RABBITMQ_CONSUMER_QUEUE,
                      body=json.dumps(message))
print(" [x] Sent 'Hello World!'")
connection.close()
