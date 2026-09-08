"""
Embedding model wrapper.

Primary path: sentence-transformers (real semantic embeddings), cached after
first load. If the model weights are not already cached locally and no
network path to download them is available (a realistic condition in an
air-gapped/sovereign deployment that hasn't pre-downloaded a model), we fall
back to a deterministic, fully local hashing-based embedding so RAG keeps
working without any external call. This fallback is weaker semantically but
requires zero downloads and zero network access — consistent with the
sovereign/offline design goal. Callers can check `embedding_mode()`.
"""
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import HashingVectorizer
from config.settings import EMBEDDING_MODEL_NAME

_model = None
_mode = None  # "sentence_transformer" | "local_hashing"
_hasher = HashingVectorizer(n_features=384, alternate_sign=False, norm="l2")


def _try_load_sentence_transformer():
    global _model
    try:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return True
    except Exception:
        _model = None
        return False


def get_embedding_model():
    global _model, _mode
    if _mode is None:
        if _try_load_sentence_transformer():
            _mode = "sentence_transformer"
        else:
            _mode = "local_hashing"
    return _model


def embedding_mode() -> str:
    get_embedding_model()
    return _mode


def embed_texts(texts: list) -> list:
    get_embedding_model()
    if _mode == "sentence_transformer":
        return _model.encode(texts, show_progress_bar=False).tolist()
    # Local hashing fallback — no downloads, fully on-device.
    vectors = _hasher.transform(texts)
    return vectors.toarray().tolist()
