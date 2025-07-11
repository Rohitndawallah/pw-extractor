import requests
import json
from pathlib import Path

from core.token_manager import load_access_token
from core.headers import get_default_headers

BATCHES_URL = "https://api.penpencil.co/batch-service/v1/batches/purchased-batches?amount=paid&page=1&type=ALL"
BATCHES_FILE = Path("data/batches.json")

def fetch_purchased_batches() -> list[dict]:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found. Please authenticate first.")

    headers = get_default_headers(token)
    response = requests.get(BATCHES_URL, headers=headers)
    response.raise_for_status()

    data = response.json().get("data", [])
    batches = [
        {
            "id": batch["_id"],
            "name": batch["name"],
            "slug": batch["slug"]
        }
        for batch in data
    ]
    return batches

def save_batches_to_file(batches: list[dict]):
    BATCHES_FILE.parent.mkdir(exist_ok=True)
    with open(BATCHES_FILE, "w", encoding="utf-8") as f:
        json.dump(batches, f, indent=2, ensure_ascii=False)

def get_saved_batches() -> list[dict]:
    if BATCHES_FILE.exists():
        with open(BATCHES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
