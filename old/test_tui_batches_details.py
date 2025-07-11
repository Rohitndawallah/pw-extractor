# test_tui_batch_details.py

from core.batches import get_saved_batches
from core.batch_details import fetch_batch_details, save_subjects
from core.token_manager import load_access_token
from core.auth import verify_token

def select_batch(batches: list[dict]) -> dict:
    print("\nAvailable Batches:")
    for i, batch in enumerate(batches, 1):
        print(f"{i}. {batch['name']}")
    choice = int(input("Select a batch (by number): "))
    return batches[choice - 1]

def main():
    print("=== Test: Fetch Batch Subject Details ===")

    token = load_access_token()
    if not token or not verify_token(token):
        print("❌ Invalid or missing token.")
        return

    batches = get_saved_batches()
    if not batches:
        print("❌ No batches found. Run test_tui_batches.py first.")
        return

    batch = select_batch(batches)
    print(f"\nFetching subject details for: {batch['name']}")

    try:
        subjects = fetch_batch_details(batch['slug'])
        save_subjects(batch['slug'], subjects)
        print(f"✅ Found {len(subjects)} subjects.\n")

        for s in subjects:
            print(f"📘 {s['subject']} (Slug: {s['slug']})")
            print(f"   🏷️ Tag Count: {s['tagCount']}, 📚 Lectures: {s['lectureCount']}, 🪪 Order: {s['displayOrder']}")
            for t in s["teacherIds"]:
                name = f"{t.get('firstName', '')} {t.get('lastName', '')}".strip()
                qual = t.get("qualification", "N/A")
                print(f"   👨‍🏫 {name} | {qual}")
            print()  # newline after each subject

    except Exception as e:
        print(f"❌ Failed to fetch subject details: {e}")

if __name__ == "__main__":
    main()
