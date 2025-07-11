# core/dpp_results.py

import requests
import json
from pathlib import Path

from core.token_manager import load_access_token
from core.headers import get_default_headers

TESTS_URL = "https://api.penpencil.co/v3/test-service/tests/dpp"
RESULT_URL = "https://api.penpencil.co/v3/test-service/tests/{test_id}/my-result"
DATA_DIR = Path("data")

def fetch_dpp_tests(batch_id: str, subject_id: str, chapter_id: str) -> list[dict]:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found.")

    headers = get_default_headers(token)
    params = {
        "page": 1,
        "limit": 50,
        "batchId": batch_id,
        "batchSubjectId": subject_id,
        "isSubjective": "false",
        "chapterId": chapter_id
    }

    response = requests.get(TESTS_URL, headers=headers, params=params)
    response.raise_for_status()

    tests = response.json().get("data", [])
    return [
        {
            "test": {
                "_id": t["test"]["_id"],
                "displayOrder": t["test"].get("displayOrder", 0),
                "name": t["test"]["name"],
                "totalMarks": t["test"]["totalMarks"],
                "totalQuestions": t["test"]["totalQuestions"]
            }
        }
        for t in tests
    ]

def fetch_test_result(test_id: str) -> dict:
    token = load_access_token()
    if not token:
        raise ValueError("No access token found.")

    headers = get_default_headers(token)
    url = RESULT_URL.format(test_id=test_id)

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json().get("data", {})
    return {
        "attempts": data.get("attemptFilter", []),
        "yourPerformance": data.get("yourPerformance", {})
    }

def _result_filename(batch_id: str, subject_id: str, test_id: str) -> Path:
    return DATA_DIR / f"result_{batch_id}_{subject_id}_{test_id}.json"

def save_dpp_result(batch_id: str, subject_id: str, test_id: str, result: dict):
    DATA_DIR.mkdir(exist_ok=True)
    path = _result_filename(batch_id, subject_id, test_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def get_saved_result(batch_id: str, subject_id: str, test_id: str) -> dict:
    path = _result_filename(batch_id, subject_id, test_id)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
