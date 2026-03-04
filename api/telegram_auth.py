import hmac
import hashlib
import urllib.parse
import json
from fastapi import HTTPException
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")


def validate_telegram_data(init_data: str):

    parsed_data = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
    hash_received = parsed_data.pop("hash", None)

    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash missing")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    hash_calculated = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if hash_calculated != hash_received:
        raise HTTPException(status_code=403, detail="Invalid Telegram signature")

    user = json.loads(parsed_data["user"])

    return user["id"]