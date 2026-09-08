"""
Simple fixed-size character chunker with overlap, preserving document/page
metadata on every chunk.
"""
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(pages: list) -> list:
    """
    pages: list of {"document","page","text"}
    returns list of {"document","page","chunk_id","text"}
    """
    chunks = []
    for p in pages:
        text = p["text"]
        step = max(CHUNK_SIZE - CHUNK_OVERLAP, 1)
        for start in range(0, len(text), step):
            piece = text[start:start + CHUNK_SIZE].strip()
            if len(piece) < 20:
                continue
            chunks.append({
                "document": p["document"],
                "page": p["page"],
                "chunk_id": f"{p['document']}_p{p['page']}_{start}",
                "text": piece,
            })
            if start + CHUNK_SIZE >= len(text):
                break
    return chunks
