"""
Model abstraction. All model adapters (local LLM, vision, api fallback)
implement this interface so the rest of the system is model-agnostic.
"""
from abc import ABC, abstractmethod


class BaseModel(ABC):
    name: str = "base"
    mode: str = "mock"  # "local" | "mock" | "api"

    @abstractmethod
    def generate(self, prompt: str, system: str = "", max_tokens: int = 512) -> str:
        """Return generated text for a prompt."""
        raise NotImplementedError

    def is_available(self) -> bool:
        return True
