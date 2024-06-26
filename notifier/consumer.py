import os
import sys
import time

import pika.exceptions

from config.config import Settings
from send.send_notification import send_email
import pika


def create_connection_and_start_consumption():
    channel = connection= None
    def callback(ch, method, properties, body):
        err = send_email(settings, body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)  # negative acknowledge
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    while True:
        try:
            # rabbitmq
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.rabbitmq_host,
                    port=settings.rabbitmq_port,
                    # virtual_host="/",
                    credentials=pika.credentials.PlainCredentials(
                        username=settings.rabbitmq_username, password=settings.rabbitmq_password,
                    ),
                )
            )
            channel = connection.channel()
            channel.basic_consume(queue="mp3", on_message_callback=callback)
            channel.start_consuming()
 
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to create connection with rabbitmq. Error: {str(e)}")
            time.sleep(2)
        except Exception as e:
            print(
                f"Failed to create connection with rabbitmq. Retrying in 2 seconds. Error: {str(e)}"
            )
            time.sleep(2)
        finally:
            try:
                if channel is not None:
                    channel.close()
                if connection and not connection.is_closed:
                    connection.close()
            except:
                pass
            
        


if __name__ == "__main__":

    settings = Settings()
    try:
        create_connection_and_start_consumption()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    