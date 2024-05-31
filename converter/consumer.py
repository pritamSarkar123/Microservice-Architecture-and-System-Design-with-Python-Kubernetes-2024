import os
import sys
import time

import gridfs
import pika
from convert import to_mp3
from config.config import Settings
from pymongo import MongoClient

def create_connection_and_start_consumption():
    channel = connection= mongo_client = None
    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)  # negative acknowledge
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    while True:
        try:
            mongo_client = MongoClient(
                f"mongodb://{settings.mongo_username}:{ settings.mongo_password}@{settings.mongo_host}:{settings.mongo_port}"
            )

            db_videos = mongo_client.videos
            db_mp3s = mongo_client.mp3s
            # gridfs
            fs_videos = gridfs.GridFS(db_videos)
            fs_mp3s = gridfs.GridFS(db_mp3s)

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
            channel.basic_consume(queue="video", on_message_callback=callback)
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
                if mongo_client is not None:
                    mongo_client.close()
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