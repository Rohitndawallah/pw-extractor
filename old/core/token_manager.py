import os
from dotenv import load_dotenv

ENV_PATH = ".env"

def save_tokens_to_env(access_token: str, expiry: str):
    with open(ENV_PATH, "w") as f:
        f.write(f"ACCESS_TOKEN={access_token}\n")
        f.write(f"TOKEN_EXPIRY={expiry}\n")

def load_access_token() -> str | None:
    load_dotenv(ENV_PATH)
    return os.getenv("ACCESS_TOKEN")

def load_token_expiry() -> str | None:
    load_dotenv(ENV_PATH)
    return os.getenv("TOKEN_EXPIRY")
