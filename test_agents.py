"""
Unit tests for individual agents using demo data and synthetic inputs.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import pytest

from core.task_manager import Task
from agents.document_agent import DocumentAgent
from agents.data_agent import DataAgent
from agents.vision_agent import VisionAgent
from agents.verification_agent import VerificationAgent
from config.settings import DEMO_DIR


def test_document_agent_extracts_pages():
    pdf_path = os.path.join(DEMO_DIR, "inspection_report.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("Demo PDF not generated.")
    task = Task(files={"pdfs": [pdf_path]})
    result = DocumentAgent().run(task)
    assert result["documents_processed"] == 1
    assert result["pages_extracted"] >= 1
    assert len(result["excerpts"]) > 0


def test_document_agent_no_files():
    task = Task(files={"pdfs": []})
    result = DocumentAgent().run(task)
    assert result["documents_processed"] == 0
    assert result["pages_extracted"] == 0


def test_data_agent_detects_threshold_exceedance(tmp_path):
    df = pd.DataFrame({
        "temperature": [70, 72, 95, 96, 97],  # threshold is 90
        "pressure": [10, 10, 10, 10, 10],
    })
    csv_path = tmp_path / "sensor.csv"
    df.to_csv(csv_path, index=False)

    task = Task(files={"csv": [str(csv_path)]})
    result = DataAgent().run(task)
    analysis = result["analysis"][str(csv_path)]
    assert analysis["fields"]["temperature"]["status"] == "ABOVE_THRESHOLD"
    assert analysis["fields"]["pressure"]["status"] == "WITHIN_RANGE"


def test_data_agent_no_files():
    task = Task(files={"csv": []})
    result = DataAgent().run(task)
    assert result["files_processed"] == 0


def test_vision_agent_mock_mode_on_missing_image():
    task = Task(files={"images": []})
    result = VisionAgent().run(task)
    assert result["images_processed"] == 0


def test_verification_agent_flags_unsupported_claim():
    task = Task()
    task.agent_results["reasoning_agent"] = {
        "possible_issues": ["[INFERENCE] Equipment will fail within 2 hours."],
        "recommendation": "Immediate shutdown required.",
        "overall_assessment": "Critical failure imminent.",
        "document_evidence": [],
        "knowledge_evidence": [],
        "vision_evidence": [],
        "data_evidence": [],
        "sources": [],
    }
    result = VerificationAgent().run(task)
    assert result["flagged"] >= 1
    assert any("UNSUPPORTED" in n or "softened" in n for n in result["notes"])


def test_verification_agent_supports_evidenced_claim():
    task = Task()
    task.agent_results["reasoning_agent"] = {
        "possible_issues": ["[INFERENCE] Possible temperature anomaly detected."],
        "recommendation": "Schedule inspection.",
        "overall_assessment": "Evidence indicates abnormal conditions.",
        "document_evidence": ["[FACT] doc evidence"],
        "knowledge_evidence": ["[FACT] kb evidence"],
        "vision_evidence": [],
        "data_evidence": ["[FACT] temp exceeded threshold"],
        "sources": ["doc.pdf — page 1"],
    }
    result = VerificationAgent().run(task)
    assert result["supported"] >= 1
    assert result["sources_available"] == 1
