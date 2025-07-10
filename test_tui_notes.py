# test_tui_notes.py

from core.batches import get_saved_batches
from core.batch_details import get_saved_subjects
from core.topics import get_saved_topics
from core.notes import fetch_notes, save_notes
from core.token_manager import load_access_token
from core.auth import verify_token

def select_batch(batches: list[dict]) -> dict:
    print("\nAvailable Batches:")
    for i, b in enumerate(batches, 1):
        print(f"{i}. {b['name']}")
    return batches[int(input("Select a batch (number): ")) - 1]

def select_subject(subjects: list[dict]) -> dict:
    print("\nAvailable Subjects:")
    for i, s in enumerate(subjects, 1):
        print(f"{i}. {s['subject']}")
    return subjects[int(input("Select a subject (number): ")) - 1]

def select_topic(topics: list[dict]) -> dict:
    print("\nAvailable Topics:")
    for i, t in enumerate(topics, 1):
        print(f"{i}. {t['name']}")
    return topics[int(input("Select a topic (number): ")) - 1]

def main():
    print("=== Test: Fetch Notes ===")

    token = load_access_token()
    if not token or not verify_token(token):
        print("❌ Invalid or missing token.")
        return

    batches = get_saved_batches()
    if not batches:
        print("❌ No batches found.")
        return
    batch = select_batch(batches)

    subjects = get_saved_subjects(batch["slug"])
    if not subjects:
        print("❌ No subjects found.")
        return
    subject = select_subject(subjects)

    topics = get_saved_topics(batch["slug"], subject["slug"])
    if not topics:
        print("❌ No topics found.")
        return
    topic = select_topic(topics)

    print(f"\n📥 Fetching notes for topic: {topic['name']}")
    try:
        notes = fetch_notes(batch["slug"], subject["slug"], topic["slug"])
        save_notes(batch["slug"], subject["slug"], topic["slug"], notes)

        print(f"✅ {len(notes)} note entries found.")
        for note in notes:
            print(f"\n📝 Topic: {note['topic']}")
            for att in note["attachments"]:
                print(f"📄 {att['name']} ➤ {att['baseUrl']}{att['key']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
