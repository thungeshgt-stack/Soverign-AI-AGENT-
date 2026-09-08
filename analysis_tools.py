"""
Higher-level analysis tool wrappers used by agents (keeps agents thin —
they call tools, tools call models/libraries).
"""
from models.vision_model import VisionModel

_vision = VisionModel()


def analyze_image(image_path: str) -> dict:
    """Tool: analyze_image() — delegates to the configured vision model adapter."""
    return _vision.analyze_image(image_path)
