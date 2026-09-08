import os
import streamlit as st
from core import state_manager as sm
from config.settings import REPORTS_DIR


def render():
    st.markdown("### 📑 Reports")
    history = sm.get("task_history")
    if not history:
        st.info("No reports generated yet. Run an analysis from New Task.")
    for task in reversed(history):
        report = task.agent_results.get("report_agent")
        if not report:
            continue
        path = report["report_path"]
        st.markdown(
            f'<div class="sovereign-card"><b>Approval Note — Task {task.task_id}</b><br>'
            f'<span style="color:var(--text-muted);font-size:13px;">{task.user_query[:100]}</span></div>',
            unsafe_allow_html=True,
        )
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(
                    f"⬇ Download {os.path.basename(path)}",
                    data=f.read(),
                    file_name=os.path.basename(path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_{task.task_id}",
                )
