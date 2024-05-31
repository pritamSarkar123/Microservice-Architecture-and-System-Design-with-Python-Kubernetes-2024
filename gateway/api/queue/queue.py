import time

import pika

from ..config import settings


def get_connections():
    channel = connection = None
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.rabbitmq_host,
                    port=settings.rabbitmq_port,
                    # virtual_host="/",
                    credentials=pika.credentials.PlainCredentials(
                        username=settings.rabbitmq_username,
                        password=settings.rabbitmq_password,
                    ),
                )
            )
            channel = connection.channel()
            print("Connection established...................")
            channel.queue_declare(queue="video", durable=True)
            channel.queue_declare(queue="mp3", durable=True)
            print("Queue declared................... video and mp3")
            break
        except Exception as e:
            print(
                f"Failed to create connection with rabbitmq. Retrying in 2 seconds. Error: {str(e)}"
            )
            channel = connection = None
            time.sleep(2)
    if channel is None or connection is None:
        raise Exception("Failed to create connection with rabbitmq")
    return channel, connection


channel, connection = get_connections()
