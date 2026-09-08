"""
Central configuration for Sovereign AI Workbench.
Loads from .env if present. Never hard-codes secrets.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Data directories ---
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "documents")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
CSV_DIR = os.path.join(DATA_DIR, "csv")
KB_DIR = os.path.join(DATA_DIR, "knowledge_base")
VECTOR_DB_DIR = os.path.join(DATA_DIR, "vector_db")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
DEMO_DIR = os.path.join(BASE_DIR, "demo")

for d in [DOCS_DIR, IMAGES_DIR, CSV_DIR, KB_DIR, VECTOR_DB_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# --- Model configuration ---
# LOCAL_LLM_MODE: "local" (open-weight model via local server) or "mock" (demo fallback)
LOCAL_LLM_MODE = os.getenv("LOCAL_LLM_MODE", "mock")
LOCAL_LLM_ENDPOINT = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:11434")  # e.g. Ollama
LOCAL_LLM_MODEL_NAME = os.getenv("LOCAL_LLM_MODEL_NAME", "qwen2.5:7b-instruct")

VISION_MODE = os.getenv("VISION_MODE", "mock")  # "local" or "mock"
VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "llava")

# Optional dev-only API fallback (never used unless explicitly enabled + key present)
ENABLE_API_FALLBACK = os.getenv("ENABLE_API_FALLBACK", "false").lower() == "true"
API_FALLBACK_KEY = os.getenv("API_FALLBACK_KEY", "")

# --- Embeddings / RAG ---
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "4"))

# --- Sensor thresholds (demo domain knowledge) ---
SENSOR_THRESHOLDS = {
    "temperature": {"max": 90.0, "unit": "°C"},
    "pressure": {"max": 12.0, "unit": "bar"},
    "vibration": {"max": 6.0, "unit": "mm/s"},
    "rpm": {"max": 3200.0, "unit": "rpm"},
}

# --- Security / sovereignty status (derived at runtime, never hard-claimed) ---
def network_isolation_status() -> str:
    """Reports configured intent, not a physical guarantee. See security/network_monitor.py."""
    if ENABLE_API_FALLBACK:
        return "EXTERNAL_API_ENABLED"
    return "LOCAL_ONLY_CONFIGURED"

APP_NAME = "SOVEREIGN AI WORKBENCH"
APP_SUBTITLE = "Private Multimodal Agentic Intelligence for Confidential Industrial Work"
