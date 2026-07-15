"""
Configuration module for the AI Content Engine.
Loads environment variables and provides API configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── OpenRouter Configuration ───────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-4o"  # Primary model for text generation
OPENROUTER_FALLBACK_MODEL = "anthropic/claude-3.5-sonnet"

# ─── GPT Image Configuration ─────────────────────────────────────────────────
# Uses OpenAI DALL-E 3 directly (GPT_IMAGE_API_KEY is an OpenAI key starting with sk-proj-)
GPT_IMAGE_API_KEY = os.getenv("GPT_IMAGE_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
GPT_IMAGE_MODEL = "dall-e-3"
GPT_IMAGE_BASE_URL = "https://api.openai.com/v1"

# ─── Runway Configuration ────────────────────────────────────────────────────
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY", "")
RUNWAY_BASE_URL = "https://api.runwayml.com/v1"

# ─── Application Defaults ────────────────────────────────────────────────────
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 120

# ─── Temperature settings ────────────────────────────────────────────────────
TEMP_CREATIVE = 0.8    # tagline, social
TEMP_PRECISE = 0.3     # blog intro (factual)
TEMP_IMAGE = 0.7       # image prompt generation

# ─── Validation ──────────────────────────────────────────────────────────────
REQUIRED_API_KEYS = {
    "OpenRouter (Text Generation)": OPENROUTER_API_KEY,
}

OPTIONAL_API_KEYS = {
    "GPT Image": GPT_IMAGE_API_KEY,
    "Runway (Video)": RUNWAY_API_KEY,
}


def validate_config() -> list[str]:
    """
    Check that all required API keys are present.
    Returns a list of missing key names (empty if all are configured).
    """
    missing = []
    for name, key in {**REQUIRED_API_KEYS}.items():
        if not key or key.startswith("your_") or key == "":
            missing.append(name)
    return missing