import os
import json
import streamlit as st

# --- Path Setup ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json(file_name):
    """Load a JSON file from the data directory."""
    path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- Load Data Sources ---
resume_data = load_json("resume.json")
candidate_text = load_json("candidate_text.json")
leetcode_data = load_json("leetcode.json")
github_data = load_json("github.json")
job_data = load_json("jd.json")  # <-- Ensure this file exists

# --- Streamlit UI ---
st.title("📊 Data Viewer")

# View selection
view_type = st.radio("Select View:", ["Candidate Viewer", "Job Viewer"])

# ---------------------------
# Candidate Viewer
# ---------------------------
if view_type == "Candidate Viewer":
    st.subheader("Candidate Data Viewer")

    person_ids = [c.get("person_id") for c in resume_data] if resume_data else []
    selected_person = st.selectbox("Select Candidate", options=person_ids)

    if selected_person:
        st.markdown(f"### Data for: `{selected_person}`")

        # Candidate Text
        st.write("#### Candidate Text")
        candidate_entry = next((c for c in candidate_text if c.get("person_id") == selected_person), {})
        st.json(candidate_entry if candidate_entry else {"info": "No candidate text data found"})

        # GitHub
        st.write("#### GitHub Data")
        github_entry = next((g for g in github_data if g.get("person_id") == selected_person), {})
        st.json(github_entry if github_entry else {"info": "No GitHub data found"})

        # LeetCode
        st.write("#### LeetCode Data")
        leetcode_entry = next((l for l in leetcode_data if l.get("person_id") == selected_person), {})
        st.json(leetcode_entry if leetcode_entry else {"info": "No LeetCode data found"})

# ---------------------------
# Job Viewer
# ---------------------------
elif view_type == "Job Viewer":
    st.subheader("Job Description Viewer")

    job_ids = [j.get("job_id") for j in job_data] if job_data else []
    selected_job = st.selectbox("Select Job ID", options=job_ids)

    if selected_job:
        st.markdown(f"### Job Data for: `{selected_job}`")
        job_entry = next((j for j in job_data if j.get("job_id") == selected_job), {})
        st.json(job_entry if job_entry else {"info": "No job data found"})
