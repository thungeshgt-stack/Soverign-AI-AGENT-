"""
Aggregates honest status of each subsystem for the Security page.
"""
from config import settings
from models.local_llm import LocalLLM
from models.vision_model import VisionModel
from rag import vector_store
from security.network_monitor import get_network_status
from rag.embeddings import embedding_mode


def get_security_status() -> dict:
    llm = LocalLLM()
    vision = VisionModel()
    net = get_network_status()

    try:
        kb_ready = not vector_store.is_empty()
    except Exception:
        kb_ready = False

    return {
        "data_processing": "LOCAL",
        "llm": {
            "mode": llm.mode,
            "status": "LOCAL / CONFIGURED" if llm.mode == "local" else "DEMO / MOCK MODE",
            "model_name": settings.LOCAL_LLM_MODEL_NAME,
        },
        "vision": {
            "mode": vision.mode,
            "status": "LOCAL / CONFIGURED" if vision.mode == "local" else "DEMO / MOCK MODE",
        },
        "knowledge_base": "LOCAL (ChromaDB, on-disk)",
        "embedding_mode": embedding_mode(),
        "vector_db_ready": kb_ready,
        "external_api": "ENABLED" if settings.ENABLE_API_FALLBACK else "DISABLED / NOT CONFIGURED",
        "network": net,
    }
