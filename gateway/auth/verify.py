from __future__ import annotations
import os, requests
from flask import Request, Response
from response import response_text
from flask_api import status
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env


def token(request: Request):
    if not "Authorization" in request.headers:
        return None, (response_text.MISSING_CREDENTIALS, status.HTTP_401_UNAUTHORIZED)
    token: str = request.headers["Authorization"]
    if not token:
        return None, (response_text.MISSING_CREDENTIALS, status.HTTP_401_UNAUTHORIZED)
    response: Response = requests.post(
        url=f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/verify",
        headers={"Authorization": token},
    )
    if response.status_code == status.HTTP_200_OK:
        return response.text, None
    return None, (response.text, response.status_code)
