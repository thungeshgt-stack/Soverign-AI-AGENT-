import streamlit as st
from security.security_status import get_security_status
from security.audit_log import format_audit_log
from core import state_manager as sm
from ui.styles import status_pill


def render():
    st.markdown("### 🔐 Security & Sovereignty")
    status = get_security_status()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div class="sovereign-card">'
            f'<div class="sovereign-card-title">Data Processing</div>{status_pill("🟢 " + status["data_processing"], "green")}<br><br>'
            f'<div class="sovereign-card-title">Model (Reasoning)</div>'
            f'{status_pill("🟢 " + status["llm"]["status"], "green" if status["llm"]["mode"]=="local" else "amber")} '
            f'<span style="color:var(--text-muted);font-size:12px;">({status["llm"]["model_name"]})</span><br><br>'
            f'<div class="sovereign-card-title">Vision Model</div>'
            f'{status_pill("🟢 " + status["vision"]["status"], "green" if status["vision"]["mode"]=="local" else "amber")}'
            f'</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="sovereign-card">'
            f'<div class="sovereign-card-title">Knowledge Base</div>{status_pill("🟢 " + status["knowledge_base"], "green")}<br><br>'
            f'<div class="sovereign-card-title">Vector Database</div>'
            f'{status_pill("🟢 READY" if status["vector_db_ready"] else "○ EMPTY", "green" if status["vector_db_ready"] else "blue")}<br><br>'
            f'<div class="sovereign-card-title">External API</div>'
            f'{status_pill("🟢 " + status["external_api"], "green" if status["external_api"]!="ENABLED" else "amber")}'
            f'</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="sovereign-card"><div class="sovereign-card-title">📡 Network Status</div>'
        f'{status_pill(status["network"]["mode"], "green" if not status["network"]["external_api_configured"] else "amber")}'
        f'<p style="color:var(--text-muted);font-size:13px;margin-top:8px;">{status["network"]["note"]}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sovereign-card" style="font-size:13.5px;color:var(--text-muted);">'
        "Sovereign deployment is designed to keep confidential organizational data, models and "
        "knowledge bases within controlled infrastructure. This status page reports application "
        "configuration honestly and does not claim a physically verified air gap unless the "
        "deployment environment is independently isolated.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Audit Log")
    task = sm.get("current_task")
    if task:
        for line in format_audit_log(task):
            st.markdown(f"`{line}`")
    else:
        st.caption("No task run yet in this session.")
