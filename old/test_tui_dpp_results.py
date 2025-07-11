# test_tui_dpp_results.py

from core.batches import get_saved_batches
from core.batch_details import get_saved_subjects
from core.topics import get_saved_topics
from core.dpp_results import fetch_dpp_tests, fetch_test_result, save_dpp_result
from core.token_manager import load_access_token
from core.auth import verify_token

def select_batch(batches: list[dict]) -> dict:
    print("\nAvailable Batches:")
    for i, batch in enumerate(batches, 1):
        print(f"{i}. {batch['name']}")
    choice = int(input("Select a batch (by number): "))
    return batches[choice - 1]

def select_subject(subjects: list[dict]) -> dict:
    print("\nAvailable Subjects:")
    for i, subject in enumerate(subjects, 1):
        print(f"{i}. {subject['subject']}")
    choice = int(input("Select a subject (by number): "))
    return subjects[choice - 1]

def select_topic(topics: list[dict]) -> dict:
    print("\nAvailable Topics:")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic['name']}")
    choice = int(input("Select a topic (by number): "))
    return topics[choice - 1]

def select_test(tests: list[dict]) -> dict:
    print("\nAvailable DPP Tests:")
    for i, t in enumerate(tests, 1):
        print(f"{i}. {t['test']['name']}")
    choice = int(input("Select a test (by number): "))
    return tests[choice - 1]['test']

def main():
    print("=== Test: DPP Test Result Fetching ===")
    
    token = load_access_token()
    if not token or not verify_token(token):
        print("❌ Invalid or missing token.")
        return

    batches = get_saved_batches()
    if not batches:
        print("❌ No batches found. Run test_tui_batches.py first.")
        return
    batch = select_batch(batches)

    subjects = get_saved_subjects(batch["slug"])
    if not subjects:
        print("❌ No subjects found. Run test_tui_batch_details.py first.")
        return
    subject = select_subject(subjects)

    topics = get_saved_topics(batch["slug"], subject["slug"])
    if not topics:
        print("❌ No topics found. Run test_tui_topics.py first.")
        return
    topic = select_topic(topics)

    try:
        print(f"\n📥 Fetching DPP tests for {topic['name']}...")
        tests = fetch_dpp_tests(batch["_id"], subject["id"], topic["_id"])
        if not tests:
            print("❌ No DPP tests found.")
            return

        test = select_test(tests)
        print(f"\n📊 Fetching result for: {test['name']}")
        result = fetch_test_result(test["_id"])
        save_dpp_result(batch["_id"], subject["id"], test["_id"], result)

        print(f"✅ Result Fetched:\nScore: {result['yourPerformance']['userScore']}/{result['yourPerformance']['totalScore']}")
        print(f"Accuracy: {result['yourPerformance']['accuracy']}%")
        print(f"Correct: {result['yourPerformance']['correctQuestions']}, Incorrect: {result['yourPerformance']['inCorrectQuestions']}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
