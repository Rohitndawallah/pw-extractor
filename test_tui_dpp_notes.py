# test_tui_dpp_notes.py

from core.batches import get_saved_batches
from core.batch_details import get_saved_subjects
from core.topics import get_saved_topics
from core.dpp_notes import fetch_dpp_notes, save_dpp_notes
from core.token_manager import load_access_token
from core.auth import verify_token

def select(items: list[dict], label: str, key: str = "name") -> dict:
    print(f"\nAvailable {label}:")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item[key]}")
    return items[int(input(f"Select {label} (number): ")) - 1]

def main():
    print("=== Test: Fetch DPP Notes ===")

    token = load_access_token()
    if not token or not verify_token(token):
        print("❌ Invalid or missing token.")
        return

    batches = get_saved_batches()
    if not batches:
        print("❌ No batches found.")
        return
    batch = select(batches, "Batch")

    subjects = get_saved_subjects(batch["slug"])
    if not subjects:
        print("❌ No subjects found.")
        return
    subject = select(subjects, "Subject", key="subject")

    topics = get_saved_topics(batch["slug"], subject["slug"])
    if not topics:
        print("❌ No topics found.")
        return
    topic = select(topics, "Topic")

    print(f"\n📥 Fetching DPP notes for topic: {topic['name']}")
    try:
        dpp_notes = fetch_dpp_notes(batch["slug"], subject["slug"], topic["slug"])
        save_dpp_notes(batch["slug"], subject["slug"], topic["slug"], dpp_notes)

        print(f"✅ {len(dpp_notes)} DPP note entries found.")
        for note in dpp_notes:
            print(f"\n📘 {note['topic']}")
            for att in note["attachments"]:
                print(f"📄 {att['name']} ➤ {att['baseUrl']}{att['key']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
