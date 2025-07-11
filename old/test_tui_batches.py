# test_tui_batches.py

from core.batches import fetch_purchased_batches, save_batches_to_file, get_saved_batches
from core.token_manager import load_access_token
from core.auth import verify_token

def main():
    print("=== Test: Fetch Purchased Batches ===")

    token = load_access_token()
    if not token:
        print("❌ No token found. Please run authentication flow first.")
        return

    print("Verifying token...")
    if not verify_token(token):
        print("❌ Token is invalid or expired. Please regenerate it.")
        return

    print("Fetching batches...")
    try:
        batches = fetch_purchased_batches()
        save_batches_to_file(batches)
        print(f"✅ Found and saved {len(batches)} batches.")
        for idx, b in enumerate(batches, 1):
            print(f"{idx}. {b['name']} (ID: {b['id']}, Slug: {b['slug']})")
    except Exception as e:
        print(f"❌ Failed to fetch batches: {e}")

if __name__ == "__main__":
    main()
