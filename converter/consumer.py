from __future__ import annotations
import sys, time
from os import environ, _exit
from pika import ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pymongo import database, MongoClient
from gridfs import GridFS
from convert import to_mp3
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


def main():
    client: MongoClient = MongoClient(
        host=environ.get("MONGO_HOST"), port=int(environ.get("MONGO_PORT"))
    )
    db_videos: database.Database = client.videos
    db_mp3s: database.Database = client.mp3s
    # GridFS MongoDB
    fs_videos: GridFS = GridFS(database=db_videos)
    fs_mp3s: GridFS = GridFS(database=db_mp3s)

    # RabbitMQ connection
    connection: BlockingConnection = BlockingConnection(
        ConnectionParameters(host="system-design-rabbitmq")
    )
    channel: BlockingChannel = connection.channel()

    def callback(ch: BlockingChannel, method, properties, body) -> None:
        err: str | None = to_mp3.start(
            message=body, fs_videos=fs_videos, fs_mp3s=fs_mp3s, channel=ch
        )
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Terminating the process...")
        try:
            sys.exit(0)
        except SystemExit:
            _exit(0)
