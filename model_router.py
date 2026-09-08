"""
Model Router: maps a task type to a configured model. Configuration-based
for the MVP (not a benchmarking system) — but built so a new model can be
plugged in without touching agent code.
"""
from models.local_llm import LocalLLM
from models.vision_model import VisionModel

_llm = LocalLLM()
_vision = VisionModel()

# task_type -> (model_instance, human_readable_reason)
ROUTES = {
    "document_summarization": (_llm, "General-purpose local LLM; strong at extraction/summarization."),
    "reasoning": (_llm, "General reasoning capability; combines multi-agent evidence."),
    "verification": (_llm, "Evidence-checking reasoning over the same local model."),
    "vision": (_vision, "Dedicated multimodal/vision adapter for image evidence."),
}


def route(task_type: str):
    """Return (model, reason) for a task type. Falls back to the reasoning model."""
    return ROUTES.get(task_type, ROUTES["reasoning"])


def router_status(task_type: str) -> dict:
    model, reason = route(task_type)
    return {
        "task": task_type,
        "selected_model": model.name,
        "mode": model.mode,
        "reason": reason,
    }
