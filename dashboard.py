"""
Main dashboard: upload inputs, enter task, run orchestrator pipeline live.
"""
import os
import streamlit as st

from config import settings
from core import state_manager as sm
from core.task_manager import Task
from core.orchestrator import run_pipeline
from tools.file_tools import save_uploaded_file
from ui.styles import status_pill

PIPELINE_LABELS = {
    "orchestrator": "Orchestrator",
    "document_agent": "Document Agent",
    "rag_agent": "RAG Knowledge Agent",
    "vision_agent": "Vision Agent",
    "data_agent": "Data Agent",
    "reasoning_agent": "Reasoning Engine",
    "verification_agent": "Verification Agent",
    "report_agent": "Report Agent",
}
STATUS_ICON = {"PENDING": "○", "RUNNING": "●", "COMPLETED": "✓", "FALLBACK": "!"}
STATUS_LEVEL = {"PENDING": "blue", "RUNNING": "amber", "COMPLETED": "green", "FALLBACK": "amber"}


def _render_system_status():
    cols = st.columns(4)
    items = [
        ("🟢 Local Processing", "Data stays on this workbench instance"),
        ("🟢 Knowledge Base", "Ready" if sm.get("kb_indexed") else "Empty — upload a PDF"),
        ("🟢 Agents Available", "6 specialized agents"),
        ("🟢 Security Mode", "Active"),
    ]
    for col, (title, sub) in zip(cols, items):
        with col:
            st.markdown(f'<div class="sovereign-card"><div class="sovereign-card-title">{title}</div>'
                        f'<div style="color:var(--text-muted);font-size:13px;">{sub}</div></div>',
                        unsafe_allow_html=True)


def _render_uploads():
    st.markdown("#### INPUT DATA")
    c1, c2, c3 = st.columns(3)

    with c1:
        pdfs = st.file_uploader("PDF documents", type=["pdf"], accept_multiple_files=True, key="pdf_up")
        if pdfs:
            for f in pdfs:
                path = save_uploaded_file(f, settings.DOCS_DIR)
                sm.get("uploaded_pdfs")[f.name] = path

    with c2:
        imgs = st.file_uploader("Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="img_up")
        if imgs:
            for f in imgs:
                path = save_uploaded_file(f, settings.IMAGES_DIR)
                sm.get("uploaded_images")[f.name] = path

    with c3:
        csvs = st.file_uploader("CSV / Excel", type=["csv"], accept_multiple_files=True, key="csv_up")
        if csvs:
            for f in csvs:
                path = save_uploaded_file(f, settings.CSV_DIR)
                sm.get("uploaded_csvs")[f.name] = path

    _render_file_cards()


def _render_file_cards():
    pdfs, imgs, csvs = sm.get("uploaded_pdfs"), sm.get("uploaded_images"), sm.get("uploaded_csvs")
    if not (pdfs or imgs or csvs):
        return
    st.markdown("&nbsp;", unsafe_allow_html=True)
    for name in pdfs:
        st.markdown(f'<div class="evidence-box">📄 <b>{name}</b> &nbsp; {status_pill("Ready to process", "blue")}</div>',
                    unsafe_allow_html=True)
    for name in imgs:
        st.markdown(f'<div class="evidence-box">🖼 <b>{name}</b> &nbsp; {status_pill("Ready for vision analysis", "blue")}</div>',
                    unsafe_allow_html=True)
    for name in csvs:
        st.markdown(f'<div class="evidence-box">📊 <b>{name}</b> &nbsp; {status_pill("Ready for data analysis", "blue")}</div>',
                    unsafe_allow_html=True)


def _build_task(query: str) -> Task:
    return Task(
        user_query=query,
        files={
            "pdfs": list(sm.get("uploaded_pdfs").values()),
            "images": list(sm.get("uploaded_images").values()),
            "csv": list(sm.get("uploaded_csvs").values()),
        },
    )


def _run_and_render(task: Task):
    st.markdown("#### AI EXECUTION PIPELINE")
    pipeline_placeholder = st.empty()
    audit_placeholder = st.empty()

    def render_pipeline():
        rows = []
        for agent_name in task.required_agents:
            status = task.agent_status.get(agent_name, "PENDING")
            label = PIPELINE_LABELS.get(agent_name, agent_name)
            detail = ""
            result = task.agent_results.get(agent_name)
            if agent_name == "document_agent" and result:
                detail = f"{result['pages_extracted']} page(s) extracted"
            elif agent_name == "rag_agent" and result:
                detail = f"{len(result.get('chunks', []))} evidence chunk(s) retrieved"
            elif agent_name == "vision_agent" and result:
                detail = f"{result['images_processed']} image(s) analyzed"
            elif agent_name == "data_agent" and result:
                detail = f"{result['files_processed']} file(s) analyzed"
            elif agent_name == "reasoning_agent" and result:
                detail = "Evidence combined into assessment"
            elif agent_name == "verification_agent" and result:
                detail = f"{result['supported']} supported / {result['flagged']} flagged"
            elif agent_name == "report_agent" and result:
                detail = "Approval note generated"
            icon = STATUS_ICON.get(status, "○")
            level = STATUS_LEVEL.get(status, "blue")
            rows.append(
                f'<div class="pipeline-row"><span class="pipeline-icon">{icon}</span>'
                f'<span class="pipeline-name">{label}</span>'
                f'<span class="pipeline-detail">{detail}</span>'
                f'<span style="margin-left:auto;">{status_pill(status, level)}</span></div>'
            )
        pipeline_placeholder.markdown("".join(rows), unsafe_allow_html=True)

    for _agent_name, _result in run_pipeline(task):
        render_pipeline()

    render_pipeline()
    audit_placeholder.markdown(
        "**Audit Log**\n\n" + "\n\n".join(f"`{ts}` {msg}" for ts, msg in task.audit_log)
    )
    sm.set("current_task", task)
    sm.get("task_history").append(task)


def _render_result_card(task: Task):
    reasoning = task.agent_results.get("reasoning_agent", {})
    verification = task.agent_results.get("verification_agent", {})
    if not reasoning:
        return

    risk = reasoning.get("risk_level", "UNKNOWN")
    risk_level_display = {"LOW": ("🟢 WITHIN RANGE", "green"),
                           "MEDIUM": ("⚠ ATTENTION REQUIRED", "amber"),
                           "HIGH": ("🔴 URGENT ATTENTION", "red")}.get(risk, ("UNKNOWN", "blue"))

    st.markdown("#### MAINTENANCE STATUS")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(
            f'<div class="sovereign-card">'
            f'<div class="sovereign-card-title">Status</div>'
            f'<div class="big-stat">{risk_level_display[0]}</div>'
            f'<div style="margin-top:8px;">Risk Level: {status_pill(risk, risk_level_display[1])}</div>'
            f'<div style="margin-top:6px;color:var(--text-muted);font-size:13px;">'
            f'Confidence: {reasoning.get("confidence")}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="sovereign-card"><div class="sovereign-card-title">Verification</div>'
            f'<div style="font-size:13.5px;">✓ Claims supported: {verification.get("supported",0)}<br>'
            f'⚠ Claims requiring caution: {verification.get("flagged",0)}<br>'
            f'✓ Sources available: {verification.get("sources_available",0)}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="sovereign-card"><div class="sovereign-card-title">Why?</div>', unsafe_allow_html=True)
        for i, issue in enumerate(reasoning.get("possible_issues", []), start=1):
            st.markdown(f"{i}. {issue}")
        st.markdown(f"**Recommendation:** {reasoning.get('recommendation')}")
        st.markdown("</div>", unsafe_allow_html=True)

    report_result = task.agent_results.get("report_agent")
    if report_result and os.path.exists(report_result["report_path"]):
        with open(report_result["report_path"], "rb") as f:
            st.download_button(
                "⬇ DOWNLOAD APPROVAL NOTE",
                data=f.read(),
                file_name=os.path.basename(report_result["report_path"]),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


def render():
    st.markdown("### Industrial Intelligence Assistant")
    st.markdown(
        '<div style="color:var(--text-muted);margin-bottom:18px;">'
        "Analyze confidential industrial documents, images and operational data "
        "using coordinated AI agents.</div>",
        unsafe_allow_html=True,
    )

    _render_system_status()
    st.markdown("---")
    _render_uploads()
    st.markdown("---")

    DEMO_QUERY = ("Analyze the equipment condition, identify possible issues, determine whether "
                  "maintenance is required, explain the evidence, and prepare an approval note.")

    default_query = st.session_state.pop("_pending_query", "")
    query = st.text_area(
        "What would you like the AI workbench to analyze?",
        value=default_query,
        placeholder="Analyze the equipment condition and determine whether maintenance is required.",
        height=90,
        key="task_query",
    )

    c1, c2 = st.columns([1, 1])
    run_clicked = c1.button("▶ START ANALYSIS", type="primary", use_container_width=True)
    demo_clicked = c2.button("▶ RUN INDUSTRIAL DEMO", use_container_width=True)

    if demo_clicked:
        from ui.demo_loader import load_demo_files
        load_demo_files()
        query = query or DEMO_QUERY
        st.session_state["_pending_query"] = query
        run_clicked = True

    if run_clicked:
        if not (sm.get("uploaded_pdfs") or sm.get("uploaded_images") or sm.get("uploaded_csvs")):
            st.warning("Upload at least one document, image, or CSV file — or use Run Industrial Demo.")
        elif not query:
            st.warning("Please describe what you'd like the workbench to analyze.")
        else:
            task = _build_task(query)
            _run_and_render(task)

    task = sm.get("current_task")
    if task and task.status == "COMPLETED":
        st.markdown("---")
        _render_result_card(task)
