"""
Dark industrial theme CSS injected once into the Streamlit app.
"""
import streamlit as st

CSS = """
<style>
:root {
    --bg-primary: #0B0F17;
    --bg-panel: #131A26;
    --bg-card: #1A2332;
    --border-subtle: #2A3648;
    --text-primary: #E5E9F0;
    --text-muted: #8B96A8;
    --accent-blue: #38BDF8;
    --accent-green: #34D399;
    --accent-amber: #FBBF24;
    --accent-red: #F87171;
}

.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

section[data-testid="stSidebar"] {
    background-color: var(--bg-panel);
    border-right: 1px solid var(--border-subtle);
}

h1, h2, h3, h4 {
    color: var(--text-primary) !important;
    font-family: 'Arial', sans-serif;
}

.sovereign-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
}

.sovereign-card-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 8px;
}

.status-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}

.status-green { background: rgba(52,211,153,0.15); color: var(--accent-green); }
.status-amber { background: rgba(251,191,36,0.15); color: var(--accent-amber); }
.status-red   { background: rgba(248,113,113,0.15); color: var(--accent-red); }
.status-blue  { background: rgba(56,189,248,0.15); color: var(--accent-blue); }

.pipeline-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 10px;
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    margin-bottom: 6px;
}

.pipeline-icon { font-size: 16px; width: 20px; text-align: center; }
.pipeline-name { font-weight: 600; font-size: 14px; }
.pipeline-detail { color: var(--text-muted); font-size: 12.5px; }

.evidence-box {
    background-color: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    font-size: 13.5px;
}

.big-stat {
    font-size: 34px;
    font-weight: 700;
    color: var(--text-primary);
}
.big-stat-label {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

hr { border-color: var(--border-subtle) !important; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def status_pill(text: str, level: str = "green") -> str:
    return f'<span class="status-pill status-{level}">{text}</span>'
