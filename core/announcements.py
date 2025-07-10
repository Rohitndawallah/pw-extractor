# core/announcements.py

import requests
import json
from pathlib import Path

from core.token_manager import load_access_token
from core.headers import get_default_headers

ANNOUNCEMENT_URL = "https://api.penpencil.co/v1/batches/{batch_id}/announcement?page=1"
DATA_DIR = Path("data")

def fetch_announcements(batch_id: str) -> list[dict]:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found. Please authenticate first.")

    headers = get_default_headers(token)
    url = ANNOUNCEMENT_URL.format(batch_id=batch_id)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json().get("data", [])
    extracted = []

    for item in data:
        attachment = item.get("attachment", {})
        extracted.append({
            "announcement": item.get("announcement", ""),
            "scheduleTime": item.get("scheduleTime", ""),
            "attachment": {
                "name": attachment.get("name", ""),
                "baseUrl": attachment.get("baseUrl", ""),
                "key": attachment.get("key", "")
            } if attachment else {}
        })

    return extracted

def _filename(batch_slug: str) -> Path:
    safe_slug = batch_slug.replace(" ", "_").replace("/", "_")
    return DATA_DIR / f"announcements_{safe_slug}.json"

def save_announcements(batch_slug: str, announcements: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    path = _filename(batch_slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(announcements, f, indent=2, ensure_ascii=False)

def get_saved_announcements(batch_slug: str) -> list[dict]:
    path = _filename(batch_slug)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
