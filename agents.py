import streamlit as st
from core import state_manager as sm
from core.orchestrator import AGENT_REGISTRY
from core.model_router import router_status

AGENT_DESCRIPTIONS = {
    "document_agent": "Extracts and chunks text from uploaded PDFs (PyMuPDF).",
    "vision_agent": "Analyzes equipment images for visible condition indicators.",
    "data_agent": "Profiles sensor CSV data, flags threshold exceedances and anomalies.",
    "reasoning_agent": "Combines all evidence into a structured, evidence-tagged assessment.",
    "verification_agent": "Checks claims against evidence; flags/softens unsupported statements.",
    "report_agent": "Generates the DOCX approval note from the verified assessment.",
}


def render():
    st.markdown("### 🤖 Agents")
    task = sm.get("current_task")
    for name, agent in AGENT_REGISTRY.items():
        status = "Not yet run"
        if task:
            status = task.agent_status.get(name, "Not yet run")
        st.markdown(
            f'<div class="sovereign-card"><b>{agent.display_name}</b> '
            f'<span style="float:right;color:var(--text-muted);">{status}</span><br>'
            f'<span style="color:var(--text-muted);font-size:13px;">{AGENT_DESCRIPTIONS.get(name,"")}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("### 🧩 Model Router")
    for task_type in ["reasoning", "vision", "verification", "document_summarization"]:
        r = router_status(task_type)
        st.markdown(
            f'<div class="sovereign-card"><b>{r["task"].replace("_"," ").title()}</b><br>'
            f'<span style="color:var(--text-muted);font-size:13px;">Selected model: {r["selected_model"]} '
            f'({r["mode"]}) — {r["reason"]}</span></div>',
            unsafe_allow_html=True,
        )
