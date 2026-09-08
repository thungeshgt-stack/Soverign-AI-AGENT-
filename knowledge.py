import streamlit as st
from rag.rag_pipeline import search_knowledge
from rag import vector_store


def render():
    st.markdown("### 🧠 Knowledge Base")
    try:
        empty = vector_store.is_empty()
    except Exception:
        empty = True

    if empty:
        st.info("Knowledge base is empty. Upload and process a PDF from New Task to index it.")
        return

    st.success("Knowledge base has indexed content.")
    q = st.text_input("Search the knowledge base", placeholder="e.g. recommended operating temperature")
    if q:
        results = search_knowledge(q, top_k=5)
        st.markdown("#### KNOWLEDGE EVIDENCE")
        for r in results:
            with st.expander(f"{r['document']} — Page {r['page']} · similarity {r.get('similarity')}"):
                st.write(r["text"])
