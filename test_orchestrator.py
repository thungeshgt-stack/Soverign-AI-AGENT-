"""
End-to-end orchestrator tests using the full demo dataset.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.task_manager import Task
from core.orchestrator import run_pipeline, plan_agents
from rag import vector_store
from config.settings import DEMO_DIR


@pytest.fixture(autouse=True)
def clean_vector_store():
    vector_store._client = None
    vector_store._collection = None
    yield
    try:
        vector_store.reset()
    except Exception:
        pass
    vector_store._client = None
    vector_store._collection = None


def _demo_files():
    return {
        "pdfs": [os.path.join(DEMO_DIR, "inspection_report.pdf"),
                 os.path.join(DEMO_DIR, "maintenance_manual.pdf")],
        "images": [os.path.join(DEMO_DIR, "equipment_image.jpg")],
        "csv": [os.path.join(DEMO_DIR, "sensor_data.csv")],
    }


def _demo_available():
    files = _demo_files()
    return all(os.path.exists(p) for group in files.values() for p in group)


def test_plan_agents_includes_all_stages_when_all_files_present():
    task = Task(files=_demo_files())
    plan = plan_agents(task)
    assert "document_agent" in plan
    assert "rag_agent" in plan
    assert "vision_agent" in plan
    assert "data_agent" in plan
    assert "reasoning_agent" in plan
    assert "verification_agent" in plan
    assert "report_agent" in plan


def test_plan_agents_skips_missing_modalities():
    task = Task(files={"pdfs": [], "images": [], "csv": []})
    plan = plan_agents(task)
    assert "document_agent" not in plan
    assert "vision_agent" not in plan
    assert "data_agent" not in plan
    # reasoning/verification/report always run
    assert "reasoning_agent" in plan
    assert "verification_agent" in plan
    assert "report_agent" in plan


def test_full_pipeline_end_to_end():
    if not _demo_available():
        pytest.skip("Demo data not generated — run demo/generate_demo_data.py first.")

    task = Task(
        user_query="Analyze the equipment condition and determine whether maintenance is required.",
        files=_demo_files(),
    )
    for _stage, _result in run_pipeline(task):
        pass

    assert task.status == "COMPLETED"
    assert task.final_result.get("risk_level") in ("LOW", "MEDIUM", "HIGH")

    reasoning = task.agent_results.get("reasoning_agent")
    assert reasoning is not None
    assert "possible_issues" in reasoning

    verification = task.agent_results.get("verification_agent")
    assert verification is not None
    assert verification["supported"] + verification["flagged"] >= 0

    report = task.agent_results.get("report_agent")
    assert report is not None
    assert os.path.exists(report["report_path"])

    # Threshold exceedance in demo sensor data should surface as elevated risk
    assert task.final_result["risk_level"] in ("MEDIUM", "HIGH")

    # Audit log should be non-empty and traceable
    assert len(task.audit_log) >= len(task.required_agents)


def test_pipeline_handles_no_files_gracefully():
    task = Task(user_query="General question with no data.", files={"pdfs": [], "images": [], "csv": []})
    for _stage, _result in run_pipeline(task):
        pass
    assert task.status == "COMPLETED"
    assert task.agent_results.get("reasoning_agent") is not None
