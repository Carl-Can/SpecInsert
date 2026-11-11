"""Runtime settings that do not import the LLM client."""

import os

PLACEHOLDER_API_KEYS = frozenset({
    "",
    "demo-key",
    "your_api_key_here",
    "sk-xxxxxxxxxxxxxxxx",
})

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
)
DEFAULT_LLM_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_LLM_MODEL = "deepseek-chat"


def is_llm_configured(key: str | None = None) -> bool:
    """True only when the key is present and not a known placeholder."""
    if key is None:
        key = os.getenv("LLM_API_KEY")
    return (key or "").strip() not in PLACEHOLDER_API_KEYS


def cors_config(raw: str | None = None) -> tuple[list[str], bool]:
    """Return (allow_origins, allow_credentials).

    A single ``*`` allows any browser origin and disables credentials,
    because browsers reject wildcard CORS together with credentialed requests.
    """
    if raw is None:
        raw = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    value = (raw or "").strip()
    if value == "*":
        return ["*"], False
    origins = [part.strip() for part in value.split(",") if part.strip()]
    return origins, True
