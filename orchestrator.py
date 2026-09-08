"""
Orchestrator: decides which agents a task needs, runs them in sequence,
updates the Task's live status/audit log so the UI can render the
execution pipeline in real time (via a generator/callback pattern).
"""
from core.task_manager import Task
from agents.document_agent import DocumentAgent
from agents.vision_agent import VisionAgent
from agents.data_agent import DataAgent
from agents.reasoning_agent import ReasoningAgent
from agents.verification_agent import VerificationAgent
from agents.report_agent import ReportAgent
from rag.rag_pipeline import index_document, search_knowledge

AGENT_REGISTRY = {
    "document_agent": DocumentAgent(),
    "vision_agent": VisionAgent(),
    "data_agent": DataAgent(),
    "reasoning_agent": ReasoningAgent(),
    "verification_agent": VerificationAgent(),
    "report_agent": ReportAgent(),
}


def plan_agents(task: Task) -> list:
    """Determine required agents based on available files. Order matters."""
    plan = ["orchestrator"]
    if task.files.get("pdfs"):
        plan.append("document_agent")
        plan.append("rag_agent")  # index + retrieve, handled inline (no separate class per structure)
    if task.files.get("images"):
        plan.append("vision_agent")
    if task.files.get("csv"):
        plan.append("data_agent")
    plan.append("reasoning_agent")
    plan.append("verification_agent")
    plan.append("report_agent")
    return plan


def run_pipeline(task: Task, generate_report: bool = True):
    """
    Generator that yields after each stage completes, so the UI can render
    live progress. Mutates `task` in place.
    """
    task.status = "RUNNING"
    task.required_agents = plan_agents(task)
    for agent_name in task.required_agents:
        task.set_status(agent_name, "PENDING")

    task.set_status("orchestrator", "COMPLETED")
    task.log(f"Task {task.task_id} created — {len(task.required_agents)-1} agent stage(s) planned.")
    yield "orchestrator", {"note": "Task decomposed"}

    if "document_agent" in task.required_agents:
        task.set_status("document_agent", "RUNNING")
        yield "document_agent", None
        result = AGENT_REGISTRY["document_agent"].run(task)
        task.agent_results["document_agent"] = result
        task.set_status("document_agent", "COMPLETED")
        task.log(f"Document Agent: {result['pages_extracted']} page(s) extracted from "
                  f"{result['documents_processed']} document(s).")
        yield "document_agent", result

    if "rag_agent" in task.required_agents:
        task.set_status("rag_agent", "RUNNING")
        yield "rag_agent", None
        indexed_chunks = 0
        for path in task.files.get("pdfs", []):
            indexed_chunks += index_document(path)
        chunks = search_knowledge(task.user_query, top_k=4) if task.user_query else []
        rag_result = {"agent": "rag_agent", "chunks_indexed": indexed_chunks, "chunks": chunks}
        task.agent_results["rag_agent"] = rag_result
        status = "COMPLETED" if chunks else "FALLBACK"
        task.set_status("rag_agent", status)
        task.log(f"RAG Knowledge Agent: {indexed_chunks} chunk(s) indexed, {len(chunks)} retrieved.")
        yield "rag_agent", rag_result

    if "vision_agent" in task.required_agents:
        task.set_status("vision_agent", "RUNNING")
        yield "vision_agent", None
        result = AGENT_REGISTRY["vision_agent"].run(task)
        task.agent_results["vision_agent"] = result
        any_mock = any(r.get("mode") == "mock" for r in result.get("results", []))
        task.set_status("vision_agent", "FALLBACK" if any_mock else "COMPLETED")
        task.log(f"Vision Agent: {result['images_processed']} image(s) analyzed"
                  f"{' (demo fallback)' if any_mock else ''}.")
        yield "vision_agent", result

    if "data_agent" in task.required_agents:
        task.set_status("data_agent", "RUNNING")
        yield "data_agent", None
        result = AGENT_REGISTRY["data_agent"].run(task)
        task.agent_results["data_agent"] = result
        task.set_status("data_agent", "COMPLETED")
        task.log(f"Data Agent: {result['files_processed']} file(s) analyzed.")
        yield "data_agent", result

    task.set_status("reasoning_agent", "RUNNING")
    yield "reasoning_agent", None
    reasoning_result = AGENT_REGISTRY["reasoning_agent"].run(task)
    task.agent_results["reasoning_agent"] = reasoning_result
    task.set_status("reasoning_agent", "FALLBACK" if reasoning_result.get("model_mode") == "mock" else "COMPLETED")
    task.log("Reasoning Engine: evidence combined into structured assessment.")
    yield "reasoning_agent", reasoning_result

    task.set_status("verification_agent", "RUNNING")
    yield "verification_agent", None
    verification_result = AGENT_REGISTRY["verification_agent"].run(task)
    task.agent_results["verification_agent"] = verification_result
    task.set_status("verification_agent", "COMPLETED")
    task.log(f"Verification Agent: {verification_result['supported']} supported, "
              f"{verification_result['flagged']} flagged.")
    yield "verification_agent", verification_result

    if generate_report:
        task.set_status("report_agent", "RUNNING")
        yield "report_agent", None
        report_result = AGENT_REGISTRY["report_agent"].run(task)
        task.agent_results["report_agent"] = report_result
        task.set_status("report_agent", "COMPLETED")
        task.log(f"Report Agent: approval note generated at {report_result['report_path']}.")
        yield "report_agent", report_result

    task.status = "COMPLETED"
    task.final_result = {
        "risk_level": reasoning_result.get("risk_level"),
        "recommendation": reasoning_result.get("recommendation"),
        "confidence": reasoning_result.get("confidence"),
    }
    task.log("Task completed.")
