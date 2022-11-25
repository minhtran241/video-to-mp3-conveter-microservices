from __future__ import annotations
import os, requests
from flask import Request
from werkzeug.datastructures import Authorization
from response import response_text
from flask_api import status
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


def login(request: Request):
    auth: Authorization | None = request.authorization
    if not auth:
        return None, (response_text.MISSING_CREDENTIALS, status.HTTP_401_UNAUTHORIZED)
    basicAuth = (auth.username, auth.password)
    response = requests.post(
        url=f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth,
    )
    if response.status_code == status.HTTP_200_OK:
        return response.text, None
    return None, (response.text, response.status_code)
