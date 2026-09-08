"""
Semantic retriever: question -> embedding -> vector search -> top chunks.
"""
from rag.embeddings import embed_texts
from rag import vector_store


def retrieve(question: str, top_k: int = 4) -> list:
    if vector_store.is_empty():
        return []
    embedding = embed_texts([question])[0]
    results = vector_store.query(embedding, top_k=top_k)
    for r in results:
        # Chroma L2 distance -> rough similarity score for display (not calibrated probability)
        r["similarity"] = round(max(0.0, 1.0 - (r["distance"] or 0) / 2), 2) if r["distance"] is not None else None
    return results
