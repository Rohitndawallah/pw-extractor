# test_tui_topics.py

from core.batches import get_saved_batches
from core.batch_details import get_saved_subjects
from core.token_manager import load_access_token
from core.auth import verify_token
from core.topics import fetch_subject_topics, save_topics

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

def main():
    print("=== Test: Fetch Subject Topics ===")

    token = load_access_token()
    if not token or not verify_token(token):
        print("❌ Invalid or missing token.")
        return

    batches = get_saved_batches()
    if not batches:
        print("❌ No batches found. Run test_tui_batches.py.")
        return

    batch = select_batch(batches)
    subjects = get_saved_subjects(batch["slug"])
    if not subjects:
        print("❌ No subjects found. Run test_tui_batch_details.py.")
        return

    subject = select_subject(subjects)

    print(f"\nFetching topics for {subject['subject']} in batch {batch['name']}")

    try:
        topics = fetch_subject_topics(batch["slug"], subject["slug"])
        save_topics(batch["slug"], subject["slug"], topics)
        print(f"✅ Found {len(topics)} topics.\n")

        for t in topics:
            print(f"📘 {t['name']} (Slug: {t['slug']})")
            print(f"   📝 Notes: {t['notes']} | 📹 Videos: {t['videos']} | 🎞️ Lectures: {t['lectureVideos']} | 🧠 Exercises: {t['exercises']}")
    except Exception as e:
        print(f"❌ Failed to fetch topics: {e}")

if __name__ == "__main__":
    main()
