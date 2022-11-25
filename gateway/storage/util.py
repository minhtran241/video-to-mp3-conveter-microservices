from os import environ
from typing import Dict, Any
from werkzeug.datastructures import FileStorage
from gridfs import GridFS
from pika.adapters.blocking_connection import BlockingChannel
from flask import Response
from pika import spec, BasicProperties
from response import response_text
from flask_api import status
import json
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


def upload(
    f: FileStorage, fs: GridFS, channel: BlockingChannel, access: Any
) -> Response:
    try:
        # put the files into MongoDB GridFS
        fid: Any = fs.put(data=f)
    except Exception as err:
        return (
            response_text.INTERNAL_SERVER_ERROR,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    message: Dict[str, Any] = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }
    try:
        # produce message
        channel.basic_publish(
            exchange="",
            routing_key=environ.get("VIDEO_QUEUE"),
            body=json.dumps(obj=message),
            properties=BasicProperties(delivery_mode=spec.PERSISTENT_DELIVERY_MODE),
        )
    except:
        fs.delete(file_id=fid)
        return (
            response_text.INTERNAL_SERVER_ERROR,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
