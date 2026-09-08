"""
Loads documents (currently PDF) into page-level text for chunking.
"""
from tools.pdf_tools import read_pdf


def load_pdf_pages(path: str) -> list:
    """Return list of {"document","page","text"}."""
    return read_pdf(path)
