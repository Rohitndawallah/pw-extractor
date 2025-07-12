# cli.py

import os
import json
import time
import random
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv, set_key
from core.auth_api import send_otp, get_token, verify_token
from core.fetch_data import (
    get_purchased_batches,
    get_batch_subjects,
    get_subject_topics,
    get_topic_notes,
    get_dpp_notes,
    # get_dpp_quizzes,
    # get_dpp_quiz_solution
)


# Constants
ENV_PATH = Path("data/.env")
USER_INFO_FILE = Path("data/user_info.json")


def ensure_data_folder():
    os.makedirs("data", exist_ok=True)
    if not ENV_PATH.exists():
        ENV_PATH.touch()


def save_token_to_env(token: str):
    set_key(dotenv_path=ENV_PATH, key_to_set="TOKEN", value_to_set=token)
    print("[INFO] Access token saved to data/.env")


def load_token_from_env() -> str:
    load_dotenv(dotenv_path=ENV_PATH)
    token = os.getenv("TOKEN")
    if not token:
        print("[ERROR] No token found. Please generate a token first.")
        return None
    print(token)
    return token


def save_user_info(username: str, country_code: str, token_expiry: int):
    info = {
        "username": username,
        "country_code": country_code,
        "token_expiry": token_expiry
    }
    with open(USER_INFO_FILE, "w") as f:
        json.dump(info, f, indent=2)
    print("[INFO] User info saved to data/user_info.json")


def generate_token_flow():
    print("\n--- Generate Token ---")
    username = input("Enter phone number: ").strip()
    country_code = input("Enter country code (e.g. +91): ").strip()

    print("[DEBUG] Sending OTP...")
    success, result = send_otp(username, country_code)
    if not success:
        print(f"[ERROR] {result['message']} (Status: {result['status']})")
        return

    otp = getpass("Enter OTP: ").strip()
    print("[DEBUG] Verifying OTP and generating token...")
    success, result = get_token(username, otp)
    if not success:
        print(f"[ERROR] {result['message']} (Status: {result['status']})")
        return

    token = result["access_token"]
    expiry = result["expires_in"]
    save_token_to_env(token)
    save_user_info(username, country_code, expiry)
    print("[SUCCESS] Token generation complete.")


def verify_token_flow():
    print("\n--- Verify Token ---")
    print("[DEBUG] Verifying token...")

    success, result = verify_token()
    if success:
        print("[SUCCESS] Token is valid.")
    else:
        print(f"[ERROR] {result['message']} (Status: {result['status']})")


def fetch_data_flow(refetch_all: bool = False):
    print("\n--- Fetch Data ---")

    def delay():
        sleep_time = random.randint(1, 5)
        print(f"[INFO] Sleeping for {sleep_time} seconds to avoid rate-limiting...\n")
        time.sleep(sleep_time)

    fetched_data_file = Path("data/fetched_data.json")
    fetched_data = {}
    if fetched_data_file.exists():
        with open(fetched_data_file, "r") as f:
            fetched_data = json.load(f)

    # Step 1: Get all purchased batches
    delay()
    print("[STEP] Fetching purchased batches...")
    batches = get_purchased_batches()

    for batch in batches:
        slug = batch["slug"]
        batch_id = batch["id"]
        print(f"[BATCH] Processing '{slug}'")

        if not refetch_all and slug in fetched_data:
            print(f"[SKIP] Batch '{slug}' already fetched. Skipping...")
            continue

        delay()
        print(f"[STEP] Fetching subjects for batch '{slug}'...")
        subjects = get_batch_subjects(slug)

        fetched_data[slug] = {}

        for subject in subjects:
            subject_slug = subject["slug"]
            subject_id = subject["id"]
            print(f"  [SUBJECT] Processing '{subject_slug}'")

            delay()
            print(f"  [STEP] Fetching topics for subject '{subject_slug}'...")
            topics = get_subject_topics(slug, subject_slug)

            fetched_data[slug][subject_slug] = []

            for topic in topics:
                topic_slug = topic["slug"]
                topic_id = topic["id"]
                print(f"    [TOPIC] Processing '{topic_slug}'")

                # Notes
                delay()
                print(f"    [NOTES] Fetching topic notes...")
                get_topic_notes(slug, subject_slug, topic_slug)

                # DPP PDFs
                delay()
                print(f"    [DPP] Fetching DPP notes...")
                get_dpp_notes(batch_id, subject_id, topic_id)

                # # DPP Quizzes
                # delay()
                # print(f"    [QUIZ] Fetching DPP quizzes...")
                # quizzes = get_dpp_quizzes(batch_id, subject_id, topic_id)

                # if isinstance(quizzes, list):
                #     for quiz in quizzes:
                #         attempt_id = quiz.get("attemptId")
                #         if attempt_id:
                #             delay()
                #             print(f"      [SOLUTION] Fetching solution for quiz attempt ID {attempt_id}...")
                #             get_dpp_quiz_solution(attempt_id)

                fetched_data[slug][subject_slug].append(topic_slug)

    # Save fetched tracking
    with open(fetched_data_file, "w") as f:
        json.dump(fetched_data, f, indent=2)

    print("\n[SUCCESS] Data fetching complete. All information saved.")





def download_data_flow():
    print("\n--- Download Data ---")
    print("[INFO] This feature is not implemented yet.")


def main():
    ensure_data_folder()
    while True:
        print("\n===== PW CLI Dashboard =====")
        print("1. Generate Token")
        print("2. Verify Token")
        print("3. Fetch Data")
        print("4. Download Data")
        print("5. Exit")

        choice = input("Select an option (1-5): ").strip()
        if choice == "1":
            generate_token_flow()
        elif choice == "2":
            verify_token_flow()
        elif choice == "3":
            fetch_data_flow()
        elif choice == "4":
            download_data_flow()
        elif choice == "5":
            print("Exiting. Goodbye.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main()
