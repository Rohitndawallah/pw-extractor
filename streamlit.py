import os
import streamlit as st
from core.generate_token import send_otp, get_token
from core.utils import verify_token
from core.content import fetch_batches, fetch_subjects, fetch_topics, fetch_notes, fetch_dpp
from dotenv import load_dotenv
import zipfile
import io
import requests

# --- Constants ---
DATA_DIR = "data"
TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
os.makedirs(DATA_DIR, exist_ok=True)
load_dotenv()

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    return None

def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def check_token(token):
    if token:
        res = verify_token(token)
        return res.get("success", False)
    return False

def zip_files(file_dict):
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w') as zf:
        for filename, url in file_dict.items():
            try:
                resp = requests.get(url)
                if resp.ok:
                    zf.writestr(filename, resp.content)
            except Exception:
                continue
    mem_zip.seek(0)
    return mem_zip

# -- Prefetch batches/subjects/topics all-at-once on login --
@st.cache_data(show_spinner=False)
def prefetch_all_batches_subjects_topics(token):
    batches_raw = fetch_batches(token)
    batches_list = []
    if isinstance(batches_raw, dict) and "batches" in batches_raw:
        batches_list = batches_raw["batches"]
    elif isinstance(batches_raw, list):
        batches_list = batches_raw

    result = {}  # {batch_id: {'batch':{}, 'subjects':{subject_id:{'subject':{}, 'topics':{topic_id:topic}}}}}
    for batch in batches_list:
        batch_id = batch.get('_id') or batch.get('id') or batch.get('slug')
        batch_slug = batch.get('slug')
        subjects = fetch_subjects(token, batch_slug)
        subj_dict = {}
        for subj in subjects:
            subject_id = subj.get('_id') or subj.get('id') or subj.get('slug')
            subj_slug = subj.get('slug')
            topics = fetch_topics(token, batch_slug, subj_slug)
            topic_dict = {}
            for topic in topics:
                topic_id = topic.get('_id') or topic.get('id') or topic.get('slug')
                topic_dict[topic_id] = topic
            subj_dict[subject_id] = {
                'subject': subj,
                'topics': topic_dict
            }
        result[batch_id] = {
            'batch': batch,
            'subjects': subj_dict
        }
    return result

def main():
    st.set_page_config("PW Batch Dashboard", layout="wide")
    token = load_token()
    if 'otp_sent' not in st.session_state:
        st.session_state["otp_sent"] = False

    # ---- LOGIN PAGE ----
    if not token or not check_token(token):
        st.title("Login to PW Dashboard")
        left, right = st.columns(2)

        # LEFT: OTP login
        with left:
            st.subheader("Login via OTP")
            cc = st.text_input("Country Code", value="+91", max_chars=5)
            phone = st.text_input("Phone Number")
            if st.button("Send OTP"):
                if phone and cc:
                    resp = send_otp(phone, cc)
                    if resp.get("success"):
                        st.session_state["otp_sent"] = True
                        st.success("OTP sent to your phone.")
                    else:
                        st.error(resp.get("error_message", "Failed to send OTP."))
                        st.session_state["otp_sent"] = False
                else:
                    st.warning("Please enter both country code and phone number.")
            if st.session_state["otp_sent"]:
                otp = st.text_input("Enter OTP")
                if st.button("Verify OTP & Login"):
                    if otp:
                        tkres = get_token(phone, otp)
                        if tkres.get("success"):
                            save_token(tkres["access_token"])
                            st.success("Login successful. Redirecting…")
                            st.session_state.clear()
                            st.rerun()
                        else:
                            st.error(tkres.get("error_message", "Invalid OTP"))
                    else:
                        st.warning("Please enter the OTP.")

        # RIGHT: Paste token
        with right:
            st.subheader("Use Existing Access Token")
            input_token = st.text_area("Access Token", height=120)
            if st.button("Verify Token & Login"):
                if input_token.strip():
                    if check_token(input_token.strip()):
                        save_token(input_token.strip())
                        st.success("Token verified. Redirecting…")
                        st.session_state.clear()
                        st.rerun()
                    else:
                        st.error("Invalid token. Please check and try again.")
                else:
                    st.warning("Please paste your access token before verifying.")

        return

    # ---- PREFETCH ALL BATCH/SUBJECT/TOPIC TREE (ONCE) ----
    if 'all_batches' not in st.session_state:
        with st.spinner("Loading your batches, subjects and chapters..."):
            st.session_state['all_batches'] = prefetch_all_batches_subjects_topics(token)

    all_data = st.session_state.get('all_batches', {})

    if not all_data or len(all_data) == 0:
        st.warning("No batches or data found for your user.")
        if st.button("Logout"):
            delete_token()
            st.session_state.clear()
            st.rerun()
        return

    # ---- MAIN DASHBOARD ----
    st.button("Logout", on_click=lambda: (delete_token(), st.session_state.clear(), st.rerun()), key="logout-btn")
    st.title("PW Study Material Dashboard")

    # BATCH SELECTOR:
    batch_id_to_name = {bid: all_data[bid]['batch'].get('name', bid) for bid in all_data}
    batch_ids = list(batch_id_to_name.keys())
    batch_names = [batch_id_to_name[bid] for bid in batch_ids]
    if not batch_ids:
        st.warning("No batches found for your account.")
        return
    selected_batch_idx = st.selectbox("Select Batch", range(len(batch_names)), format_func=lambda i: batch_names[i])
    sel_batch_id = batch_ids[selected_batch_idx]
    sel_batch = all_data[sel_batch_id]['batch']
    sel_batch_slug = sel_batch.get('slug')

    # SUBJECT SELECTOR:
    subjects_dict = all_data[sel_batch_id]['subjects']
    subject_id_to_name = {sid: subjects_dict[sid]['subject'].get('subject', sid) for sid in subjects_dict}
    subject_ids = list(subject_id_to_name.keys())
    subject_names = [subject_id_to_name[sid] for sid in subject_ids]
    if not subject_ids:
        st.warning("No subjects found for the selected batch.")
        return
    selected_subject_idx = st.selectbox("Select Subject", range(len(subject_names)), format_func=lambda i: subject_names[i])
    sel_subject_id = subject_ids[selected_subject_idx]
    sel_subject = subjects_dict[sel_subject_id]['subject']
    sel_subject_slug = sel_subject.get('slug')

    # TOPIC SELECTOR:
    topics_dict = subjects_dict[sel_subject_id]['topics']
    topic_id_to_name = {tid: topics_dict[tid].get('name', tid) for tid in topics_dict}
    topic_ids = list(topic_id_to_name.keys())
    topic_names = [topic_id_to_name[tid] for tid in topic_ids]
    if not topic_ids:
        st.info("No topics for this subject.")
        return
    selected_topic_idx = st.selectbox("Select Topic/Chapter", range(len(topic_names)), format_func=lambda i: topic_names[i])
    sel_topic_id = topic_ids[selected_topic_idx]
    sel_topic = topics_dict[sel_topic_id]
    sel_topic_slug = sel_topic.get('slug')
    topic_name = sel_topic.get('name')

    # RADIO SELECTOR FOR CONTENT TYPE:
    tab = st.radio(
        "Select Content Type",
        ["Notes", "DPP", "DPP-Quiz", "Announcements"],
        horizontal=True
    )

    file_dict = dict()

    # --- NOTES TAB ---
    if tab == "Notes":
        notes = fetch_notes(token, sel_batch_slug, sel_subject_slug, sel_topic_slug)
        st.subheader(f"Notes for Topic: {topic_name}")
        if notes:
            col1, col2, col3 = st.columns([7, 1, 1])
            col1.write("Name")
            col2.write("View")
            col3.write("Download")
            for entry in reversed(notes):
                topic_display = entry.get("topic") or "Untitled"
                for att in entry.get("attachments", []):
                    filename = att.get("name") or f"{topic_display}.pdf"
                    url = att.get("baseUrl", "").rstrip("/") + "/" + att.get("key", "").lstrip("/")
                    cols = st.columns([7, 1, 1])
                    cols[0].write(filename)
                    cols[1].markdown(f'[Link]({url})', unsafe_allow_html=True)
                    try:
                        resp = requests.get(url)
                        if resp.ok:
                            cols[2].download_button("Download", resp.content, file_name=filename, mime="application/pdf")
                        else:
                            cols[2].write("Unavailable")
                    except Exception:
                        cols[2].write("Unavailable")
                    file_dict[filename] = url
            if file_dict:
                if st.button("Download All Notes as ZIP"):
                    mem_zip = zip_files(file_dict)
                    st.download_button("Download All Notes", mem_zip, file_name=f"{topic_name}_notes.zip")
        else:
            st.info("No notes found for this topic.")

    # --- DPP TAB ---
    elif tab == "DPP":
        dpp = fetch_dpp(token, sel_batch_slug, sel_subject_slug, sel_topic_slug)
        st.subheader(f"DPPs for Topic: {topic_name}")
        if dpp:
            col1, col2, col3 = st.columns([7, 1, 1])
            col1.write("Name")
            col2.write("View")
            col3.write("Download")
            for entry in reversed(dpp):
                topic_display = entry.get("topic") or "Untitled"
                for att in entry.get("attachments", []):
                    filename = att.get("name") or f"{topic_display}.pdf"
                    url = att.get("baseUrl", "").rstrip("/") + "/" + att.get("key", "").lstrip("/")
                    cols = st.columns([7, 1, 1])
                    cols[0].write(filename)
                    cols[1].markdown(f'[Link]({url})', unsafe_allow_html=True)
                    try:
                        resp = requests.get(url)
                        if resp.ok:
                            cols[2].download_button("Download", resp.content, file_name=filename, mime="application/pdf")
                        else:
                            cols[2].write("Unavailable")
                    except Exception:
                        cols[2].write("Unavailable")
                    file_dict[filename] = url
            if file_dict:
                if st.button("Download All DPPs as ZIP"):
                    mem_zip = zip_files(file_dict)
                    st.download_button("Download All DPPs", mem_zip, file_name=f"{topic_name}_dpp.zip")
        else:
            st.info("No DPPs found for this topic.")

    # --- DPP QUIZ/ANNOUNCEMENTS ---
    elif tab == "DPP-Quiz":
        st.info("Upcoming feature: DPP-Quiz downloads/view will be available soon.")
    elif tab == "Announcements":
        st.info("Upcoming feature: Announcements will be shown here soon.")

if __name__ == "__main__":
    main()
