import streamlit as st
from core import state_manager as sm
from tools.pdf_tools import pdf_page_count


def render():
    st.markdown("### 📄 Documents")
    pdfs = sm.get("uploaded_pdfs")
    if not pdfs:
        st.info("No documents uploaded yet. Go to New Task to upload PDFs.")
        return
    for name, path in pdfs.items():
        try:
            pages = pdf_page_count(path)
        except Exception:
            pages = "?"
        st.markdown(
            f'<div class="sovereign-card"><b>📄 {name}</b><br>'
            f'<span style="color:var(--text-muted);font-size:13px;">{pages} page(s) · {path}</span></div>',
            unsafe_allow_html=True,
        )
