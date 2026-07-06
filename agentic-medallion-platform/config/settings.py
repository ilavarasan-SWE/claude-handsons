"""
Application settings.

In future versions, these values can be loaded from
environment variables or a .env file.
"""

# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------

APP_NAME = "Agentic Medallion Platform"

APP_VERSION = "1.0.0"

# ------------------------------------------------------------------
# LLM Configuration
# ------------------------------------------------------------------

OLLAMA_MODEL = "llama3.2:3b"

OLLAMA_BASE_URL = "http://localhost:11434"

TEMPERATURE = 0.0

# ------------------------------------------------------------------
# Profiling Configuration
# ------------------------------------------------------------------

MAX_SAMPLE_VALUES = 5

MAX_AI_SAMPLE_VALUES = 5

QUALITY_SCORE_MAX = 100