"""
End-to-end RAG indexing pipeline: PDF -> pages -> chunks -> embeddings -> vector store.
"""
from rag.document_loader import load_pdf_pages
from rag.chunker import chunk_pages
from rag.embeddings import embed_texts
from rag import vector_store
from rag.retriever import retrieve


def index_document(path: str) -> int:
    """Index a single PDF into the vector store. Returns number of chunks indexed."""
    pages = load_pdf_pages(path)
    chunks = chunk_pages(pages)
    if not chunks:
        return 0
    embeddings = embed_texts([c["text"] for c in chunks])
    vector_store.add_chunks(chunks, embeddings)
    return len(chunks)


def search_knowledge(question: str, top_k: int = 4) -> list:
    """Tool: search_knowledge() — semantic retrieval over the indexed knowledge base."""
    return retrieve(question, top_k=top_k)
