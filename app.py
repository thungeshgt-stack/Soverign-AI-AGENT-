import streamlit as st

from config import settings
from core import state_manager as sm
from ui.styles import inject_css, status_pill
from ui import dashboard, documents, knowledge, agents, analysis, reports, security

st.set_page_config(
    page_title=settings.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

sm.init_state()
inject_css()

NAV_SECTIONS = {
    "WORKSPACE": [
        ("💬 New Task", "new_task"),
        ("📄 Documents", "documents"),
        ("🧠 Knowledge Base", "knowledge"),
        ("📊 Data Analysis", "data_analysis"),
        ("🖼 Vision Analysis", "vision_analysis"),
    ],
    "AI SYSTEM": [
        ("🤖 Agents & 🧩 Models", "agents"),
    ],
    "OUTPUT": [
        ("📑 Reports", "reports"),
    ],
    "SECURITY": [
        ("🔐 Security & 📡 Network", "security"),
    ],
}

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "new_task"

with st.sidebar:
    st.markdown("## 🛡️ SOVEREIGN AI\nWORKBENCH")
    st.caption("On-premise agentic intelligence")
    st.markdown("---")

    for section, items in NAV_SECTIONS.items():
        st.markdown(f"**{section}**")
        for label, key in items:
            btn_type = "primary" if st.session_state["active_page"] == key else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
                st.session_state["active_page"] = key
        st.markdown("")

active = st.session_state["active_page"]

# ---- Header ----
header_l, header_r = st.columns([4, 1])
with header_l:
    st.markdown(f"# {settings.APP_NAME}")
    st.caption(settings.APP_SUBTITLE)
with header_r:
    st.markdown(
        f'<div style="text-align:right;margin-top:10px;">{status_pill("🟢 SOVEREIGN MODE", "green")}<br>'
        f'<span style="color:var(--text-muted);font-size:12px;">LOCAL PROCESSING</span></div>',
        unsafe_allow_html=True,
    )
st.markdown("---")

# ---- Route ----
ROUTES = {
    "new_task": dashboard.render,
    "documents": documents.render,
    "knowledge": knowledge.render,
    "data_analysis": analysis.render,
    "vision_analysis": analysis.render,
    "agents": agents.render,
    "reports": reports.render,
    "security": security.render,
}
ROUTES.get(active, dashboard.render)()
