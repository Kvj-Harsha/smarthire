import streamlit as st
from app.orchestrator import list_profiles, list_jds, run_orch

st.set_page_config(page_title="Meta Recruit AI", page_icon="🤖", layout="centered")

# --- Header ---
st.title("Meta Recruit AI – Multi-Agent Recruitment System")
st.markdown("""
Meta Recruit AI is an intelligent recruitment assistant developed for the **MetaUpSpace LLP AI Intern Task**.  
It integrates four core agents:
- Candidate Profiler – Extracts skills and career trajectory.  
- Technical Assessment Designer – Generates tailored challenges.  
- Behavioral & Cultural Analyzer – Evaluates soft skills.  
- Market Intelligence Optimizer – Provides compensation benchmarks.  
---
""")

# --- Load Profiles & JDs ---
profiles = list_profiles()
jds = list_jds()

if not profiles:
    st.error("No candidate profiles found in `data/resume.json`.")
elif not jds:
    st.error("No job descriptions found in `data/jd.json`.")
else:
    # --- State Initialization ---
    if "selected_profile" not in st.session_state:
        st.session_state["selected_profile"] = None
    if "selected_job" not in st.session_state:
        st.session_state["selected_job"] = None
    if "report" not in st.session_state:
        st.session_state["report"] = None

    # --- Candidate & Job Selection ---
    st.session_state["selected_profile"] = st.selectbox(
        "Select a candidate profile",
        profiles,
        index=profiles.index(st.session_state["selected_profile"])
        if st.session_state["selected_profile"] in profiles else 0
    )

    st.session_state["selected_job"] = st.selectbox(
        "Select a job description",
        jds,
        index=jds.index(st.session_state["selected_job"])
        if st.session_state["selected_job"] in jds else 0
    )

    # --- Action Buttons ---
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Run Analysis", use_container_width=True):
            with st.spinner(f"Running analysis for {st.session_state['selected_profile']} against {st.session_state['selected_job']}..."):
                st.session_state["report"] = run_orch(
                    person_id=st.session_state["selected_profile"],
                    job_id=st.session_state["selected_job"]
                )
            # Temporary toast notification instead of static success
            st.toast("✅ Orchestration done!", icon="✅")
    with col2:
        if st.button("Clear Results", type="secondary", use_container_width=True):
            st.session_state["report"] = None
            st.success("Results cleared.")

    # --- Navigation (only if report exists) ---
    if st.session_state.get("report"):
        st.markdown("### Next Steps")
        nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

        with nav_col1:
            if st.button("Candidate Profile", type="secondary", use_container_width=True):
                st.switch_page("pages/profile.py")

        with nav_col2:
            if st.button("Assessment Package", type="secondary", use_container_width=True):
                st.switch_page("pages/assessment.py")

        with nav_col3:
            if st.button("Behavioral Analysis", type="secondary", use_container_width=True):
                st.switch_page("pages/behaviour.py")

        with nav_col4:
            if st.button("Market Intelligence", type="secondary", use_container_width=True):
                st.switch_page("pages/market.py")
