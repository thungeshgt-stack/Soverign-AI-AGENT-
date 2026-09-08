"""
Thin wrapper around Streamlit session_state so UI modules don't repeat
key-existence checks. Kept intentionally simple for a one-day MVP.
"""
import streamlit as st


DEFAULTS = {
    "uploaded_pdfs": {},      # name -> path
    "uploaded_images": {},    # name -> path
    "uploaded_csvs": {},      # name -> path
    "kb_indexed": [],         # list of doc names indexed into vector store
    "current_task": None,     # Task instance
    "task_history": [],       # list of completed Task instances
    "vector_store_ready": False,
}


def init_state():
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v.copy() if isinstance(v, (dict, list)) else v


def get(key):
    init_state()
    return st.session_state.get(key)


def set(key, value):
    st.session_state[key] = value


def reset_task_state():
    st.session_state["current_task"] = None
