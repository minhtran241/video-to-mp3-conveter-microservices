from __future__ import annotations
import json, tempfile, os
from gridfs import GridFS, GridOut
from bson.objectid import ObjectId
from moviepy import editor
from pika import spec, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


def start(
    message, fs_videos: GridFS, fs_mp3s: GridFS, channel: BlockingChannel
) -> str | None:
    message = json.loads(s=message)

    # empty temporary file
    tf: tempfile._TemporaryFileWrapper = tempfile.NamedTemporaryFile()
    # video contents
    out: GridOut = fs_videos.get(file_id=ObjectId(message["video_fid"]))
    # add video contents to empty file
    tf.write(out.read())
    # create audio from temporary video file
    audio: editor.AudioFileClip | None = editor.VideoFileClip(filename=tf.name).audio
    tf.close()

    # write audio to the file
    tf_path: str = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to MongoDB
    f = open(tf_path, "rb")
    data: bytes = f.read()
    fid = fs_mp3s.put(data=data)
    f.close()
    os.remove(path=tf_path)

    message["mp3_fid"] = str(fid)
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(obj=message),
            properties=BasicProperties(delivery_mode=spec.PERSISTENT_DELIVERY_MODE),
        )
    except Exception as err:
        fs_mp3s.delete(file_id=fid)
        return f"failed to publish message: {err}"
