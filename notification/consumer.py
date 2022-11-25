from __future__ import annotations
import sys
from os import environ, _exit
from pika import ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from send import email
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


def main():
    # RabbitMQ connection
    connection: BlockingConnection = BlockingConnection(
        ConnectionParameters(host="system-design-rabbitmq")
    )
    channel: BlockingChannel = connection.channel()

    def callback(ch: BlockingChannel, method, properties, body) -> None:
        err: str | None = email.notification(message=body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=environ.get("MP3_QUEUE"), on_message_callback=callback)

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
