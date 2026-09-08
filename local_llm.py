"""
Adapter for a local open-weight LLM (e.g. served via Ollama at
LOCAL_LLM_ENDPOINT, model LOCAL_LLM_MODEL_NAME — Qwen/Llama/Mistral-family).

If LOCAL_LLM_MODE=mock or the local server is unreachable, falls back to a
deterministic, clearly-labeled mock generator so the workbench keeps working
without any model installed. Mock output is never presented as real model
reasoning in the UI — callers must check `.mode`.
"""
import requests
from models.base_model import BaseModel
from config import settings


class LocalLLM(BaseModel):
    name = "local_llm"

    def __init__(self):
        self.mode = settings.LOCAL_LLM_MODE  # "local" or "mock"
        self.endpoint = settings.LOCAL_LLM_ENDPOINT
        self.model_name = settings.LOCAL_LLM_MODEL_NAME

    def is_available(self) -> bool:
        if self.mode != "local":
            return False
        try:
            r = requests.get(f"{self.endpoint}/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system: str = "", max_tokens: int = 512) -> str:
        if self.mode == "local" and self.is_available():
            try:
                payload = {
                    "model": self.model_name,
                    "prompt": f"{system}\n\n{prompt}" if system else prompt,
                    "stream": False,
                }
                r = requests.post(f"{self.endpoint}/api/generate", json=payload, timeout=60)
                r.raise_for_status()
                return r.json().get("response", "").strip()
            except Exception as e:
                return self._mock(prompt, note=f"[local model call failed: {e}]")
        return self._mock(prompt)

    def _mock(self, prompt: str, note: str = "") -> str:
        """Deterministic demo-mode reasoning text. Clearly labeled as mock."""
        return (
            "[MOCK MODE — no local model configured] "
            f"{note} Reasoning synthesized from structured evidence rather than a "
            "live model call. Configure LOCAL_LLM_MODE=local with an Ollama endpoint "
            "to use a real open-weight model."
        )
