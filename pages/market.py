import streamlit as st
import pandas as pd

st.set_page_config(page_title="Market Intelligence", page_icon="📈", layout="wide")
st.title("📈 Market Intelligence & Sourcing Optimizer")

if "report" not in st.session_state:
    st.error("❌ Please run an analysis first from the main app.")
else:
    market = st.session_state["report"].get("market_intelligence", {})
    if not market:
        st.warning("⚠️ No market intelligence available for this selection.")
    else:
        # Header context
        cols = st.columns(4)
        cols[0].metric("Role", market.get("role", "—"))
        cols[1].metric("Location", market.get("location", "—"))
        cols[2].metric("Seniority", market.get("seniority", "—"))
        cols[3].metric("Updated", market.get("updated_at", "—"))

        st.markdown("---")

        # Compensation
        st.subheader("💰 Compensation Benchmarks (INR, LPA)")
        comp = market.get("compensation", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("p25", comp.get("p25", "—"))
        c2.metric("Median", comp.get("median", "—"))
        c3.metric("p75", comp.get("p75", "—"))
        c4.metric("Samples", comp.get("sample_size", 0))

        # Trends
        st.subheader("📊 Talent Trends")
        trends = market.get("talent_trends", {})
        t1, t2 = st.columns(2)
        t1.metric("Total Openings", trends.get("total_openings", 0))
        t2.metric("Avg Talent Supply Index", round(trends.get("avg_talent_supply_index", 0.0), 2))

        hotspots = trends.get("hotspots", [])
        if hotspots:
            df_hotspots = pd.DataFrame(hotspots)
            st.caption("Top Locations by Openings")
            st.dataframe(df_hotspots, use_container_width=True)

        # Channels
        st.subheader("🔎 Recommended Sourcing Channels")
        channels = market.get("recommended_channels", [])
        if channels:
            df_channels = pd.DataFrame(channels)
            st.dataframe(df_channels, use_container_width=True)
        else:
            st.info("No channels found for this filter.")

        # AI Summary
        ai_summary = market.get("ai_summary", {})
        st.subheader("🧭 Market Summary")
        st.success(ai_summary.get("summary", "—"))

        recs = ai_summary.get("recommendations", [])
        if recs:
            st.markdown("### 📌 Recommendations")
            for i, rec in enumerate(recs, 1):
                st.markdown(f"- {rec}")
