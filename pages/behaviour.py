import streamlit as st

st.set_page_config(page_title="Behavioral Analysis", layout="wide")

st.title("Behavioral & Cultural Fit Analysis")

# --- Guard Clause ---
if "report" not in st.session_state:
    st.error("Please run an analysis first from the main app.")
else:
    report = st.session_state["report"].get("behavioral_analysis", {})

    if not report:
        st.warning("No behavioral analysis available.")
    else:
        # --- Soft Skills Section ---
        st.subheader("Soft Skills Analysis")
        soft_skills = report.get("soft_skill_analysis", {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Collaboration", value="✔️")
            st.caption(soft_skills.get("collaboration", ""))
        with col2:
            st.metric(label="Problem-Solving", value="✔️")
            st.caption(soft_skills.get("problem_solving", ""))
        with col3:
            st.metric(label="Communication", value="✔️")
            st.caption(soft_skills.get("communication", ""))

        st.divider()

        # --- Keywords ---
        st.subheader("Key Behavioral Keywords")
        keywords = report.get("keywords", [])
        if keywords:
            st.write(", ".join([f"`{kw}`" for kw in keywords]))
        else:
            st.info("No keywords extracted.")

        st.divider()

        # --- Themes ---
        st.subheader("Behavioral Themes")
        themes = report.get("themes", [])
        if themes:
            st.write(", ".join([f"**{th}**" for th in themes]))
        else:
            st.info("No themes detected.")

        st.divider()

        # --- High-Level Insights ---
        st.subheader("High-Level Insights")
        st.success(report.get("high_level_insights", "No insights available."))

        st.divider()

        # --- Bias Mitigation Protocol ---
        st.subheader("Bias Mitigation Protocol")
        guidelines = report.get("bias_mitigation_protocol", {}).get("guidelines", [])
        if guidelines:
            for idx, g in enumerate(guidelines, 1):
                st.write(f"{idx}. {g}")
        else:
            st.info("No bias mitigation guidelines provided.")

        st.divider()

        # --- Navigation Button ---
        st.subheader("Next Step")
        if st.button("Go to Market Intelligence", type="primary", use_container_width=True):
            st.switch_page("pages/market.py")
