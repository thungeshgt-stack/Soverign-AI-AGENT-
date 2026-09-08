import streamlit as st
from core import state_manager as sm
from tools.chart_tools import generate_chart
from tools.csv_tools import read_csv


def render():
    st.markdown("### 📊 Data Analysis")
    csvs = sm.get("uploaded_csvs")
    if not csvs:
        st.info("No CSV uploaded yet. Go to New Task to upload sensor data.")
    for name, path in csvs.items():
        st.markdown(f"**{name}**")
        try:
            df = read_csv(path)
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            cols = st.columns(min(len(numeric_cols), 3) or 1)
            for i, field in enumerate(numeric_cols):
                fig = generate_chart(df, field)
                if fig:
                    with cols[i % len(cols)]:
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Could not analyze {name}: {e}")

    st.markdown("---")
    st.markdown("### 🖼 Vision Analysis")
    task = sm.get("current_task")
    vision_result = task.agent_results.get("vision_agent") if task else None
    imgs = sm.get("uploaded_images")
    if not imgs:
        st.info("No image uploaded yet.")
    for name, path in imgs.items():
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(path, caption=name, use_container_width=True)
        with c2:
            if vision_result:
                for r in vision_result.get("results", []):
                    st.markdown("**VISION FINDINGS**")
                    for obs in r.get("observations", []):
                        st.markdown(f"- {obs}")
                    st.markdown(f"Confidence: {r.get('confidence')}")
                    st.markdown(f"Recommendation: {r.get('recommendation')}")
            else:
                st.caption("Run an analysis from New Task to see vision findings here.")
