import os
import json
import requests
from dotenv import load_dotenv
from core.auth_api import verify_token, _get_auth_headers

DATA_FILE = "data/fetched_data.json"


def read_data_file():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def write_data_file(data: dict):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=2)


def _save_to_json(key: str, value):
    data = read_data_file()
    data[key] = value
    write_data_file(data)


def get_purchased_batches():
    is_verified, _ = verify_token()
    if not is_verified:
        return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

    url = "https://api.penpencil.co/batch-service/v1/batches/purchased-batches?amount=paid&page=1&type=ALL"
    headers = _get_auth_headers()
    response = requests.get(url, headers=headers)

    if not response.ok or not response.json().get("success"):
        return {"message": "Failed to fetch purchased batches."}

    batches = []
    for batch in response.json()["data"]:
        batches.append({
            "id": batch["_id"],
            "type": batch["type"],
            "name": batch["name"],
            "slug": batch["slug"],
            "startDate": batch["startDate"],
            "endDate": batch["endDate"]
        })

    _save_to_json("batches", batches)
    return batches


def get_batch_subjects(batch_slug: str):
    is_verified, _ = verify_token()
    if not is_verified:
        return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

    url = f"https://api.penpencil.co/v3/batches/{batch_slug}/details"
    headers = _get_auth_headers()
    response = requests.get(url, headers=headers)

    if not response.ok or not response.json().get("success"):
        return {"message": "Failed to fetch batch subjects."}

    subjects = []
    for sub in response.json()["data"].get("subjects", []):
        subject = {
            "id": sub["_id"],
            "name": sub["subject"],
            "slug": sub["slug"],
            "tagCount": sub["tagCount"],
            "displayOrder": sub["displayOrder"],
            "lectureCount": sub["lectureCount"],
            "teachers": []
        }
        for teacher in sub.get("teacherIds", []):
            subject["teachers"].append({
                "firstName": teacher.get("firstName"),
                "lastName": teacher.get("lastName"),
                "experience": teacher.get("experience"),
                "qualification": teacher.get("qualification"),
                "email": teacher.get("email")
            })
        subjects.append(subject)

    _save_to_json(f"subjects_{batch_slug}", subjects)
    return subjects


# def get_subject_topics(batch_slug: str, subject_slug: str):
#     is_verified, _ = verify_token()
#     if not is_verified:
#         return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

#     url = f"https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/topics?page=1"
#     headers = _get_auth_headers()
#     response = requests.get(url, headers=headers)

#     if not response.ok or not response.json().get("success"):
#         return {"message": "Failed to fetch subject topics."}

#     topics = []
#     for topic in response.json()["data"]:
#         topics.append({
#             "name": topic["name"],
#             "id": topic["typeId"],
#             "slug": topic["slug"],
#             "displayOrder": topic["displayOrder"],
#             "notes": topic["notes"],
#             "exercises": topic["exercises"],
#             "videos": topic["videos"],
#             "lectureVideos": topic["lectureVideos"]
#         })

#     _save_to_json(f"topics_{batch_slug}_{subject_slug}", topics)
#     return topics

def get_subject_topics(batch_slug: str, subject_slug: str):
    is_verified, _ = verify_token()
    if not is_verified:
        return []

    url = f"https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/topics?page=1"
    headers = _get_auth_headers()
    response = requests.get(url, headers=headers)

    if not response.ok or not response.json().get("success"):
        print(f"[ERROR] Failed to fetch topics for {batch_slug}/{subject_slug}")
        return []

    topics = []
    for topic in response.json()["data"]:
        topics.append({
            "id": topic["_id"],  # ✅ corrected from typeId
            "name": topic["name"],
            "displayOrder": topic["displayOrder"],
            "notes": topic["notes"],
            "exercises": topic["exercises"],
            "videos": topic["videos"],
            "lectureVideos": topic["lectureVideos"],
            "slug": topic["slug"]
        })

    _save_to_json(f"topics_{batch_slug}_{subject_slug}", topics)
    return topics



def get_topic_notes(batch_slug: str, subject_slug: str, topic_slug: str):
    is_verified, _ = verify_token()
    if not is_verified:
        return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

    url = f"https://api.penpencil.co/v2/batches/{batch_slug}/subject/{subject_slug}/contents?page=1&contentType=notes&tag={topic_slug}"
    headers = _get_auth_headers()
    response = requests.get(url, headers=headers)

    if not response.ok or not response.json().get("success"):
        return {"message": "Failed to fetch topic notes."}

    notes = []
    for item in response.json()["data"]:
        for hw in item.get("homeworkIds", []):
            for attachment in hw.get("attachmentIds", []):
                notes.append({
                    "topic": hw.get("topic"),
                    "note": hw.get("note"),
                    "fileName": attachment["name"],
                    "baseUrl": attachment["baseUrl"],
                    "key": attachment["key"]
                })

    _save_to_json(f"notes_{batch_slug}_{subject_slug}_{topic_slug}", notes)
    return notes


def get_dpp_notes(batch_id: str, subject_id: str, chapter_id: str):
    is_verified, _ = verify_token()
    if not is_verified:
        return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

    url = f"https://api.penpencil.co/v2/batches/{batch_id}/subject/{subject_id}/contents?page=1&contentType=DppNotes&tag={chapter_id}"
    headers = _get_auth_headers()
    response = requests.get(url, headers=headers)

    if not response.ok or not response.json().get("success"):
        return {"message": "Failed to fetch DPP notes."}

    dpps = []
    for item in response.json()["data"]:
        for hw in item.get("homeworkIds", []):
            for attachment in hw.get("attachmentIds", []):
                dpps.append({
                    "topic": hw.get("topic"),
                    "note": hw.get("note"),
                    "fileName": attachment["name"],
                    "baseUrl": attachment["baseUrl"],
                    "key": attachment["key"]
                })

    _save_to_json(f"dpp_notes_{batch_id}_{subject_id}_{chapter_id}", dpps)
    return dpps


# def get_dpp_quizzes(batch_id: str, subject_id: str, chapter_id: str):
#     is_verified, _ = verify_token()
#     if not is_verified:
#         return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

#     url = f"https://api.penpencil.co/v3/test-service/tests/dpp?page=1&limit=50&batchId={batch_id}&batchSubjectId={subject_id}&isSubjective=false&chapterId={chapter_id}"
#     headers = _get_auth_headers()
#     response = requests.get(url, headers=headers)

#     if not response.ok or not response.json().get("success"):
#         return {"message": "Failed to fetch DPP quizzes."}

#     quizzes = []
#     for item in response.json()["data"]:
#         quizzes.append({
#             "name": item["test"]["name"],
#             "totalMarks": item["test"]["totalMarks"],
#             "totalQuestions": item["test"]["totalQuestions"],
#             "attemptId": item["testStudentMapping"]["_id"]
#         })

#     _save_to_json(f"dpp_quizzes_{batch_id}_{subject_id}_{chapter_id}", quizzes)
#     return quizzes


# def get_dpp_quiz_solution(attempt_id: str):
#     is_verified, _ = verify_token()
#     if not is_verified:
#         return {"message": "Token is invalid or expired. Please reverify or regenerate it."}

#     url = f"https://api.penpencil.co/v3/test-service/tests/mapping/{attempt_id}/preview-test"
#     headers = _get_auth_headers()
#     response = requests.get(url, headers=headers)

#     if not response.ok or not response.json().get("success"):
#         return {"message": "Failed to fetch DPP quiz solution."}

#     data = response.json()["data"]
#     quiz_info = []
#     for section in data["sections"]:
#         for subject in section.get("subjects", []):
#             subject_name = subject["subjectId"]["name"]
#             for chapter in subject["chapters"]:
#                 chapter_name = chapter["chapterId"]["name"]
#                 chapter_questions = chapter["totalQuestions"]
#                 for topic in chapter["topics"]:
#                     topic_name = topic["topicId"]["name"]
#                     topic_questions = topic["totalQuestions"]
#                     for sub in topic["subTopics"]:
#                         quiz_info.append({
#                             "subjectName": subject_name,
#                             "chapterName": chapter_name,
#                             "chapterTotalQuestions": chapter_questions,
#                             "topicName": topic_name,
#                             "topicTotalQuestions": topic_questions,
#                             "subtopicName": sub["subTopicId"]["name"],
#                             "subtopicTotalQuestions": sub["totalQuestions"]
#                         })

#     questions = []
#     for q in data["questions"]:
#         qdata = q["question"]
#         image = qdata.get("imageIds", {}).get("en", {})
#         solution_img = (qdata.get("solutionDescription", [{}])[0]
#                         .get("imageIds", {}).get("en", {}))
#         questions.append({
#             "questionNumber": qdata["questionNumber"],
#             "questionType": qdata["type"],
#             "positiveMarks": qdata["positiveMarks"],
#             "negativeMarks": qdata["negativeMarks"],
#             "difficultyLevel": qdata["difficultyLevel"],
#             "topicName": qdata["topicId"]["name"],
#             "options": [opt["texts"]["en"] for opt in qdata["options"]],
#             "solutionId": qdata["solutions"][0],
#             "fileName": image.get("name"),
#             "baseUrl": image.get("baseUrl"),
#             "key": image.get("key"),
#             "solutionDescription": {
#                 "name": solution_img.get("name"),
#                 "baseUrl": solution_img.get("baseUrl"),
#                 "key": solution_img.get("key")
#             }
#         })

#     result = {
#         "info": quiz_info,
#         "questions": questions
#     }

#     _save_to_json(f"quiz_solution_{attempt_id}", result)
#     return result
