import requests
import json
from pathlib import Path

from core.token_manager import load_access_token
from core.headers import get_default_headers

DETAILS_URL = "https://api.penpencil.co/v3/batches/{slug}/details"
DATA_DIR = Path("data")

def fetch_batch_details(slug: str) -> list[dict]:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found. Please authenticate first.")

    headers = get_default_headers(token)
    url = DETAILS_URL.format(slug=slug)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    subjects = response.json().get("data", {}).get("subjects", [])
    extracted = []

    for subject in subjects:
        teachers = [
            {
                "_id": t.get("_id", ""),
                "firstName": t.get("firstName", ""),
                "lastName": t.get("lastName", ""),
                "experience": t.get("experience", ""),
                "qualification": t.get("qualification", ""),
                "email": t.get("email", "")
            }
            for t in subject.get("teacherIds", [])
        ]

        extracted.append({
            "_id": subject.get("_id", ""),
            "subject": subject.get("subject", ""),
            "slug": subject.get("slug", ""),
            "teacherIds": teachers,
            "tagCount": subject.get("tagCount", 0),
            "displayOrder": subject.get("displayOrder", 0),
            "lectureCount": subject.get("lectureCount", 0)
        })

    return extracted

def _slug_to_filename(slug: str) -> Path:
    safe_slug = slug.replace(" ", "_").replace("/", "_").replace("\\", "_")
    return DATA_DIR / f"subjects_{safe_slug}.json"

def save_subjects(slug: str, subjects: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    path = _slug_to_filename(slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(subjects, f, indent=2, ensure_ascii=False)

def get_saved_subjects(slug: str) -> list[dict]:
    path = _slug_to_filename(slug)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
