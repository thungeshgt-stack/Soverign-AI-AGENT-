"""
Reports configured network intent honestly. Does NOT claim physical
air-gapping — only reports what the application is configured to do.
"""
from config import settings


def get_network_status() -> dict:
    external_enabled = settings.ENABLE_API_FALLBACK
    return {
        "external_api_configured": external_enabled,
        "mode": "EXTERNAL_API_ENABLED" if external_enabled else "LOCAL_ONLY_CONFIGURED",
        "note": (
            "External API fallback is enabled in configuration."
            if external_enabled else
            "No external API is configured. The application is set to operate using "
            "local components only. This reflects application configuration, not a "
            "verified network-level air gap."
        ),
    }
