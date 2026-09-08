"""
PDF extraction tools using PyMuPDF (fitz). Real extraction — not a
model-imagined summary.
"""
import os
import fitz  # PyMuPDF


def read_pdf(path: str) -> list:
    """
    Extract text page by page.
    Returns list of {"document": name, "page": n, "text": str}
    """
    doc_name = os.path.basename(path)
    pages = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"document": doc_name, "page": i, "text": text})
    return pages


def pdf_page_count(path: str) -> int:
    with fitz.open(path) as doc:
        return doc.page_count
