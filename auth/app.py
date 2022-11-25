from __future__ import annotations
import jwt, datetime, os
import response
from typing import List, Dict, Any
from werkzeug.datastructures import Authorization
from flask import Flask, request
from flask_mysqldb import MySQL
from flask_api import status
from dotenv import load_dotenv

app = Flask(__name__)
mysql = MySQL(app)

# config
load_dotenv()  # take environment variables from .env.

app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
app.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

app.config["JWT_SECRET"] = os.environ.get("JWT_SECRET")

app.config["SERVER_HOST"] = os.environ.get("SERVER_HOST")
app.config["SERVER_PORT"] = os.environ.get("SERVER_PORT")


@app.route("/login", methods=["POST"])
def login():
    auth: Authorization | None = request.authorization
    if not auth:
        return response.MISSING_CREDENTIALS, status.HTTP_401_UNAUTHORIZED
    # check db for username ans password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM users WHERE email=%s", (auth.username,)
    )
    if res > 0:
        user_row: List[Any] = cur.fetchone()
        email: str = user_row[0]
        password: str = user_row[1]
        cur.close()

        if not auth.username.__eq__(email) or not auth.password.__eq__(password):
            return response.INVALID_CREDENTIALS, status.HTTP_401_UNAUTHORIZED
        return (
            encode_jwt(
                username=auth.username,
                secret=app.config["JWT_SECRET"],
                authz=True,
            ),
            status.HTTP_200_OK,
        )
    return response.INVALID_CREDENTIALS, status.HTTP_401_UNAUTHORIZED


@app.route("/verify", methods=["POST"])
def verify():
    encoded_jwt: str = request.headers["Authorization"]
    if not encoded_jwt:
        return response.MISSING_CREDENTIALS, status.HTTP_401_UNAUTHORIZED
    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded: Dict[str, Any] = jwt.decode(
            jwt=encoded_jwt, key=app.config["JWT_SECRET"], algorithms=["HS256"]
        )
    except:
        return response.UNAUTHORIZED, status.HTTP_403_FORBIDDEN
    return decoded, status.HTTP_200_OK


def encode_jwt(username: str, secret: str, authz: bool) -> str:
    return jwt.encode(
        payload={
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "is_admin": authz,
        },
        key=secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    app.run(host=app.config["SERVER_HOST"], port=app.config["SERVER_PORT"])
