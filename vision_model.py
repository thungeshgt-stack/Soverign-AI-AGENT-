"""
Vision model adapter. Supports a local multimodal model (e.g. LLaVA via
Ollama) or a clearly labeled DEMO/FALLBACK mode that performs lightweight
heuristic image analysis (brightness / edge statistics via Pillow) rather
than claiming a trained industrial diagnostic model.
"""
import requests
import base64
from PIL import Image, ImageFilter
import numpy as np

from models.base_model import BaseModel
from config import settings


class VisionModel(BaseModel):
    name = "vision_model"

    def __init__(self):
        self.mode = settings.VISION_MODE  # "local" or "mock"
        self.endpoint = settings.LOCAL_LLM_ENDPOINT
        self.model_name = settings.VISION_MODEL_NAME

    def is_available(self) -> bool:
        if self.mode != "local":
            return False
        try:
            r = requests.get(f"{self.endpoint}/api/tags", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system: str = "", max_tokens: int = 512) -> str:
        # Text-only passthrough not typical for vision model; kept for interface parity.
        return self.analyze_image_path(prompt)

    def analyze_image(self, image_path: str) -> dict:
        if self.mode == "local" and self.is_available():
            try:
                with open(image_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                payload = {
                    "model": self.model_name,
                    "prompt": "Describe visible condition of this industrial equipment: "
                              "corrosion, surface damage, leakage, cracks, abnormalities.",
                    "images": [img_b64],
                    "stream": False,
                }
                r = requests.post(f"{self.endpoint}/api/generate", json=payload, timeout=60)
                r.raise_for_status()
                text = r.json().get("response", "").strip()
                return {
                    "mode": "local",
                    "model": self.model_name,
                    "observations": [text],
                    "confidence": "model-reported",
                    "recommendation": "Requires human inspection to confirm AI-assisted finding.",
                }
            except Exception as e:
                return self._mock_analysis(image_path, note=f"local vision call failed: {e}")
        return self._mock_analysis(image_path)

    def _mock_analysis(self, image_path: str, note: str = "") -> dict:
        """
        Heuristic DEMO fallback: uses basic pixel statistics (darkness spots,
        edge density) to produce plausible, clearly-labeled demo observations.
        This is NOT a trained industrial diagnostic model.
        """
        observations = []
        try:
            img = Image.open(image_path).convert("L")
            arr = np.array(img, dtype=np.float32)
            edges = np.array(img.filter(ImageFilter.FIND_EDGES), dtype=np.float32)
            edge_density = float((edges > 40).mean())
            darkness_ratio = float((arr < 60).mean())

            if edge_density > 0.12:
                observations.append("Elevated edge/texture irregularity detected — "
                                     "possible surface damage or corrosion pattern.")
            else:
                observations.append("Surface texture appears relatively uniform in this frame.")

            if darkness_ratio > 0.15:
                observations.append("Localized dark regions detected — "
                                     "possible staining, leakage-like discoloration, or shadow.")
            else:
                observations.append("No significant dark/staining regions detected.")

        except Exception:
            observations = ["Unable to process image for demo analysis (unsupported or corrupt file)."]

        return {
            "mode": "mock",
            "model": "demo-heuristic-fallback",
            "note": note or "DEMO MODE: heuristic pixel-statistics analysis, not a trained "
                             "industrial vision model. Configure VISION_MODE=local for a real model.",
            "observations": observations,
            "confidence": "Demo / Model dependent",
            "recommendation": "Requires human inspection to confirm any AI-assisted finding.",
        }

    def analyze_image_path(self, image_path: str) -> dict:
        return self.analyze_image(image_path)
