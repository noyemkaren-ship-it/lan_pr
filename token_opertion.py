import jwt
from fastapi import Request
import secrets
SECRET_KEY = secrets.token_urlsafe(32)

def get_current_user(request: Request):
    token = request.cookies.get("token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user")
    except:
        return None