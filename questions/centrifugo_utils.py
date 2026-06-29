import jwt, time
from django.conf import settings

def get_centrifugo_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + 3600
    }
    return jwt.encode(payload, settings.CENTRIFUGO_TOKEN_KEY, algorithm="HS256")