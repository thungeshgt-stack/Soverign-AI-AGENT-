"""
Local vector store using ChromaDB (persisted to disk under
config.VECTOR_DB_DIR). All operations stay on-disk / in-process — no
external network calls.
"""
import chromadb
from config.settings import VECTOR_DB_DIR

_client = None
_collection = None
COLLECTION_NAME = "industrial_knowledge"


def get_collection():
    global _client, _collection
    if _client is None:
        _client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    if _collection is None:
        _collection = _client.get_or_create_collection(COLLECTION_NAME)
    return _collection


def add_chunks(chunks: list, embeddings: list):
    if not chunks:
        return
    collection = get_collection()
    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=[c["text"] for c in chunks],
        metadatas=[{"document": c["document"], "page": c["page"]} for c in chunks],
    )


def query(embedding: list, top_k: int = 4) -> list:
    collection = get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_embeddings=[embedding], n_results=min(top_k, collection.count()))
    out = []
    for i in range(len(results["ids"][0])):
        out.append({
            "document": results["metadatas"][0][i]["document"],
            "page": results["metadatas"][0][i]["page"],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })
    return out


def is_empty() -> bool:
    return get_collection().count() == 0


def reset():
    global _client, _collection
    if _client is not None:
        _client.delete_collection(COLLECTION_NAME)
    _collection = None
