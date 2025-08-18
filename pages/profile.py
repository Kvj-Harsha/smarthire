import streamlit as st

st.set_page_config(page_title="Candidate Profile", layout="wide")

st.title("Candidate Profile Insights")

# --- Check if report exists ---
if "report" not in st.session_state:
    st.error("Please go back to Home and run an analysis first.")
    st.page_link("app.py", label="Back to Home", icon="⬅️")
else:
    profile_id = st.session_state["selected_profile"]
    tir = st.session_state["report"]["tir"]

    profile = tir.get("profile", {})
    education = tir.get("education", [])
    yoe = tir.get("YOE", "N/A")
    work_history = tir.get("work_history", [])
    career_summary = tir.get("career_summary", "")
    skills = tir.get("skills_analysis", [])
    projects = tir.get("projects", [])
    ai_insights = tir.get("ai_insights", "")
    online_activity = tir.get("online_activity", {})

    # --- Candidate Overview ---
    st.subheader("Candidate Overview")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.write(f"**Name:** {profile.get('name','N/A')}")
        st.write(f"**Email:** {profile.get('email','N/A')}")
        st.write(f"**Years of Experience:** {yoe}")
    with col2:
        sp = profile.get("social_profiles", {})
        st.write("**Social Profiles:**")
        if sp.get("linkedin"): st.write(f"- [LinkedIn]({sp['linkedin']})")
        if sp.get("github"): st.write(f"- [GitHub]({sp['github']})")
        if sp.get("leetcode"): st.write(f"- [LeetCode]({sp['leetcode']})")

    st.divider()

    # --- Education + Career Summary ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Education")
        if education:
            for edu in education:
                st.write(f"**{edu['degree']}** — {edu['institution']} ({edu['year_of_graduation']})")
                if edu.get("cgpa"):
                    st.caption(f"CGPA: {edu['cgpa']}")
        else:
            st.info("No education details found.")

    with col2:
        st.subheader("Career Summary")
        st.write(career_summary if career_summary else "No summary available.")

    st.divider()

    # --- Work History ---
    st.subheader("Work History")
    if work_history:
        for job in work_history:
            st.write(f"- **{job.get('title','N/A')}** @ {job.get('company','N/A')} ({job.get('years','N/A')})")
            if job.get("description"):
                st.caption(job.get("description"))
    else:
        st.info("No work history found.")

    st.divider()

    # --- Skills ---
    st.subheader("Skills Analysis")
    if skills:
        skill_cols = st.columns(4)
        for i, skill in enumerate(skills):
            with skill_cols[i % 4]:
                st.metric(label=skill["skill"], value=f"{int(skill['confidence']*100)}%")
    else:
        st.info("No skills data available.")

    st.divider()

    # --- Projects ---
    st.subheader("Projects")
    if projects:
        for proj in projects:
            st.write(f"**{proj['title']}**")
            if proj.get("technologies"):
                st.caption(", ".join(proj.get("technologies", [])))
            st.write(proj.get("description", ""))
            st.markdown("---")
    else:
        st.info("No project details found.")

    st.divider()

    # --- Online Presence ---
    st.subheader("Online Presence")
    col1, col2, col3 = st.columns(3)

    with col1:
        li = online_activity.get("linkedin", {})
        st.write("**LinkedIn**")
        if li:
            st.caption(li.get("headline", ""))
            if li.get("skills"):
                st.write("Skills:", ", ".join(li["skills"]))
            for job in li.get("jobs", []):
                st.write(f"- {job.get('title','')} @ {job.get('company','')} ({job.get('years','')})")
        else:
            st.info("No LinkedIn data.")

    with col2:
        gh = online_activity.get("github", {})
        st.write("**GitHub**")
        if gh:
            st.caption(f"Repos: {gh.get('repos',0)} | ⭐ Stars: {gh.get('stars',0)}")
            if gh.get("top_languages"):
                st.write("Languages:", ", ".join(gh.get("top_languages", [])))
            if gh.get("recent_activity"):
                st.write("Recent Activity:")
                for act in gh["recent_activity"]:
                    st.write(f"- {act}")
        else:
            st.info("No GitHub data.")

    with col3:
        lc = online_activity.get("leetcode", {})
        st.write("**LeetCode**")
        if lc:
            st.metric("Problems Solved", lc.get("problems_solved", 0))
            st.metric("Contest Rating", lc.get("contest_rating", 0))
            if lc.get("strengths"):
                st.write("Strengths:", ", ".join(lc["strengths"]))
        else:
            st.info("No LeetCode data.")

    st.divider()

    # --- AI Insights ---
    st.subheader("AI Insights")
    if ai_insights:
        st.info(ai_insights)
    else:
        st.info("No AI insights available.")

    st.divider()

    # --- Navigation ---
    st.subheader("Next Steps")
    if profile_id:
        st.session_state["assessment_profile"] = profile_id
        if st.button("View Assessment Package", type="primary", use_container_width=True):
            st.switch_page("pages/assessment.py")
