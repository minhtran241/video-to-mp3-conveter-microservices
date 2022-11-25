from __future__ import annotations
import os, json
from gridfs import GridFS, GridOut
from pika import ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import verify
from auth_svc import access
from storage import util
from response import response_text
from flask_api import status
from dotenv import load_dotenv
from bson.objectid import ObjectId

app = Flask(__name__)
load_dotenv()
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")

app.config["SERVER_HOST"] = os.environ.get("SERVER_HOST")
app.config["SERVER_PORT"] = os.environ.get("SERVER_PORT")

mongo_video: PyMongo = PyMongo(app=app, uri=app.config["MONGO_URI"] + "videos")
mongo_mp3: PyMongo = PyMongo(app=app, uri=app.config["MONGO_URI"] + "mp3s")

fs_video: GridFS = GridFS(database=mongo_video.db)
fs_mp3: GridFS = GridFS(database=mongo_mp3.db)

connection: BlockingConnection = BlockingConnection(
    ConnectionParameters(host="system-design-rabbitmq")
)
channel: BlockingChannel = connection.channel()


@app.route("/login", methods=["POST"])
def login():
    token, err = access.login(request=request)
    return err if err else token, status.HTTP_200_OK


@app.route("/upload", methods=["POST"])
def upload():
    access, err = verify.token(request=request)
    if err:
        return err
    access = json.loads(s=access)
    if access["is_admin"]:
        if len(request.files) != 1:
            return response_text.ONE_FILE_REQUIRED, status.HTTP_400_BAD_REQUEST
        for _, f in request.files.items():
            err = util.upload(f=f, fs=fs_video, channel=channel, access=access)
            return err if err else response_text.SUCCESS, status.HTTP_200_OK
    else:
        return response_text.UNAUTHORIZED, status.HTTP_401_UNAUTHORIZED


@app.route("/download", methods=["GET"])
def download():
    access, err = verify.token(request=request)
    if err:
        return err
    access = json.loads(s=access)
    if access["is_admin"]:
        fid_string: str | None = request.args.get("fid")
        if not fid_string:
            return response_text.FID_REQUIRED, status.HTTP_400_BAD_REQUEST
        try:
            out: GridOut = fs_mp3.get(file_id=ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return (
                response_text.INTERNAL_SERVER_ERROR,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    return response_text.UNAUTHORIZED, status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
    app.run(host=app.config["SERVER_HOST"], port=app.config["SERVER_PORT"])
