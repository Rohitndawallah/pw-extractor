# test_tui_announcements.py

from core.batches import get_saved_batches
from core.announcements import fetch_announcements, save_announcements
from core.token_manager import load_access_token
from core.auth import verify_token

def select_batch(batches: list[dict]) -> dict:
    print("\nAvailable Batches:")
    for i, batch in enumerate(batches, 1):
        print(f"{i}. {batch['name']}")
    choice = int(input("Select a batch (by number): "))
    return batches[choice - 1]

def main():
    print("=== Test: Fetch Announcements ===")

    token = load_access_token()
    if not token or not verify_token(token):
        print("❌ Invalid or missing token.")
        return

    batches = get_saved_batches()
    if not batches:
        print("❌ No batches found.")
        return

    batch = select_batch(batches)

    batch_id = batch.get("_id") or batch.get("id")  # fallback in case it's named 'id'
    if not batch_id:
        print("❌ No batch ID found in selected batch.")
        return

    print(f"\n📣 Fetching announcements for: {batch['name']}")

    try:
        announcements = fetch_announcements(batch_id)
        save_announcements(batch["slug"], announcements)

        print(f"✅ {len(announcements)} announcement(s) saved.")
        for a in announcements:
            print(f"\n🗓️ {a['scheduleTime']}\n📢 {a['announcement']}")
            if a["attachment"]:
                print(f"📎 {a['attachment']['name']} ➤ {a['attachment']['baseUrl']}{a['attachment']['key']}")
    except Exception as e:
        print(f"❌ Failed to fetch announcements: {e}")

if __name__ == "__main__":
    main()
