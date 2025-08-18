import streamlit as st

st.set_page_config(page_title="Candidate Assessment", layout="wide")
st.title("Candidate Assessment")

# ---- Guard Clause ----
if "report" not in st.session_state:
    st.error("Please go back to Home and run an analysis first.")
    st.page_link("app.py", label="Back to Home", icon="⬅️")
else:
    profile_id = st.session_state["selected_profile"]
    assessment = st.session_state["report"]["assessment"]

    st.subheader(f"Assessment Package for **{profile_id}**")

    # ---- Render Each Problem ----
    for idx, task in enumerate(assessment, 1):

        # Difficulty badge
        diff_map = {
            "Easy": "🟢 Easy",
            "Medium": "🟡 Medium",
            "Hard": "🔴 Hard"
        }
        diff_display = diff_map.get(task.get("difficulty", ""), "⚪ Unknown")

        with st.container(border=True):  # bordered card
            st.markdown(f"### {idx}. {task['title']} ({diff_display})")
            st.write(task["description"])

            col1, col2 = st.columns([2, 1], vertical_alignment="top")

            with col1:
                with st.expander("📖 Instructions", expanded=False):
                    st.write(task.get("instructions", "No instructions available."))
                    if task.get("constraints"):
                        st.caption(f"**Constraints:** {task['constraints']}")

                with st.expander("💡 Examples", expanded=False):
                    for ex in task.get("examples", []):
                        st.code(
                            f"Input: {ex.get('input')}\nOutput: {ex.get('output')}",
                            language="python"
                        )

            with col2:
                with st.expander("⚙️ Options", expanded=False):
                    if task.get("options"):
                        st.write(f"⏱️ Time Limit: **{task['options'].get('time_limit_min','N/A')} min**")
                        st.write("💻 Languages Allowed:")
                        for lang in task["options"].get("languages_allowed", []):
                            st.write(f"- {lang}")
                    else:
                        st.write("No options available.")

        st.divider()

    # --- Navigation Button ---
    st.subheader("Next Step")
    if st.button("Go to Behavioral Analysis", type="primary", use_container_width=True):
        st.switch_page("pages/behaviour.py")
