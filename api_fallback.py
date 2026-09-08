"""
Optional development-only cloud API fallback. Disabled unless
ENABLE_API_FALLBACK=true and API_FALLBACK_KEY is set in .env.

This exists purely so developers without local GPU hardware can test the
pipeline during development. It must never be silently used in a
sovereign/offline deployment — the Security page reports its status honestly.
"""
from models.base_model import BaseModel
from config import settings


class ApiFallbackModel(BaseModel):
    name = "api_fallback"
    mode = "api"

    def is_available(self) -> bool:
        return settings.ENABLE_API_FALLBACK and bool(settings.API_FALLBACK_KEY)

    def generate(self, prompt: str, system: str = "", max_tokens: int = 512) -> str:
        if not self.is_available():
            return "[API fallback disabled — sovereign/local-only configuration]"
        # Intentionally not implemented for the MVP: no external API is called
        # unless a developer explicitly wires a provider here and enables the flag.
        return "[API fallback is enabled in config but no provider is wired in this MVP]"
