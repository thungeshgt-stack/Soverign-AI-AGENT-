"""
Tests for the RAG subsystem: chunking, indexing, and retrieval.
Uses the local hashing embedding fallback automatically if no network
access to download sentence-transformer weights is available.
"""
import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from rag.chunker import chunk_pages
from rag.rag_pipeline import index_document, search_knowledge
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


def test_chunk_pages_basic():
    pages = [{"document": "doc.pdf", "page": 1, "text": "A" * 2000}]
    chunks = chunk_pages(pages)
    assert len(chunks) > 1
    for c in chunks:
        assert c["document"] == "doc.pdf"
        assert c["page"] == 1
        assert len(c["text"]) > 0


def test_chunk_pages_skips_short_text():
    pages = [{"document": "doc.pdf", "page": 1, "text": "short"}]
    chunks = chunk_pages(pages)
    assert chunks == []


def test_index_and_retrieve_demo_pdf():
    pdf_path = os.path.join(DEMO_DIR, "maintenance_manual.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("Demo PDF not generated — run demo/generate_demo_data.py first.")
    n_chunks = index_document(pdf_path)
    assert n_chunks > 0
    assert not vector_store.is_empty()

    results = search_knowledge("recommended operating temperature", top_k=3)
    assert len(results) > 0
    assert all("document" in r and "page" in r and "text" in r for r in results)


def test_search_knowledge_empty_store_returns_empty():
    assert vector_store.is_empty()
    results = search_knowledge("anything", top_k=3)
    assert results == []
