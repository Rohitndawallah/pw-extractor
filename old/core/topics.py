# core/topics.py

import requests
import json
from pathlib import Path

from core.token_manager import load_access_token
from core.headers import get_default_headers

TOPICS_URL = "https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/topics?page=1"
DATA_DIR = Path("data")

def fetch_subject_topics(batch_slug: str, subject_slug: str) -> list[dict]:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found. Please authenticate first.")

    headers = get_default_headers(token)
    url = TOPICS_URL.format(batch_slug=batch_slug, subject_slug=subject_slug)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    topics = response.json().get("data", [])
    extracted = [
        {
            "_id": t.get("_id", ""),
            "name": t.get("name", ""),
            "displayOrder": t.get("displayOrder", 0),
            "notes": t.get("notes", 0),
            "exercises": t.get("exercises", 0),
            "videos": t.get("videos", 0),
            "lectureVideos": t.get("lectureVideos", 0),
            "slug": t.get("slug", "")
        }
        for t in topics
    ]
    return extracted

def _filename(batch_slug: str, subject_slug: str) -> Path:
    safe_batch = batch_slug.replace(" ", "_").replace("/", "_")
    safe_subject = subject_slug.replace(" ", "_").replace("/", "_")
    return DATA_DIR / f"topics_{safe_batch}__{safe_subject}.json"

def save_topics(batch_slug: str, subject_slug: str, topics: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    path = _filename(batch_slug, subject_slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)

def get_saved_topics(batch_slug: str, subject_slug: str) -> list[dict]:
    path = _filename(batch_slug, subject_slug)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
