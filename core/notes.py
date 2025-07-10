# core/notes.py

import requests
import json
from pathlib import Path

from core.token_manager import load_access_token
from core.headers import get_default_headers

NOTES_URL = "https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/contents?page=1&contentType=notes&tag={topic_slug}"
DATA_DIR = Path("data")

def fetch_notes(batch_slug: str, subject_slug: str, topic_slug: str) -> list[dict]:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found. Please authenticate first.")

    headers = get_default_headers(token)
    url = NOTES_URL.format(batch_slug=batch_slug, subject_slug=subject_slug, topic_slug=topic_slug)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    results = []
    items = response.json().get("data", [])
    
    for item in items:
        if not item.get("homeworkIds"):
            continue

        for hw in item["homeworkIds"]:
            attachments = [
                {
                    "baseUrl": a.get("baseUrl", ""),
                    "key": a.get("key", ""),
                    "name": a.get("name", "")
                }
                for a in hw.get("attachmentIds", [])
            ]

            results.append({
                "isDPPNotes": item.get("isDPPNotes", False),
                "topic": hw.get("topic", ""),
                "note": hw.get("note", ""),
                "attachments": attachments
            })

    return results

def _filename(batch_slug: str, subject_slug: str, topic_slug: str) -> Path:
    safe = lambda s: s.replace(" ", "_").replace("/", "_")
    return DATA_DIR / f"notes_{safe(batch_slug)}__{safe(subject_slug)}__{safe(topic_slug)}.json"

def save_notes(batch_slug: str, subject_slug: str, topic_slug: str, notes: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    path = _filename(batch_slug, subject_slug, topic_slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)

def get_saved_notes(batch_slug: str, subject_slug: str, topic_slug: str) -> list[dict]:
    path = _filename(batch_slug, subject_slug, topic_slug)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
