"""
Ensures tests run in deterministic mock mode by default (no network calls to
a local model server), regardless of the developer's .env settings.
"""
import os

os.environ.setdefault("LOCAL_LLM_MODE", "mock")
os.environ.setdefault("VISION_MODE", "mock")
