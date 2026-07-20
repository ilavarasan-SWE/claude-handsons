"""
Application settings.

Loads configuration from the .env file.
Provides a single source of truth for the application.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ==========================================================
# Application Configuration
# ==========================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "Agentic Medallion Platform"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)

# ==========================================================
# LLM Configuration
# ==========================================================

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        "0.0"
    )
)

# ==========================================================
# Data Profiling Configuration
# ==========================================================

MAX_SAMPLE_VALUES = int(
    os.getenv(
        "MAX_SAMPLE_VALUES",
        "5"
    )
)

MAX_AI_SAMPLE_VALUES = int(
    os.getenv(
        "MAX_AI_SAMPLE_VALUES",
        "5"
    )
)

QUALITY_SCORE_MAX = int(
    os.getenv(
        "QUALITY_SCORE_MAX",
        "100"
    )
)

# ==========================================================
# Logging Configuration
# ==========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)

LOG_FILE = os.getenv(
    "LOG_FILE",
    "logs/application.log"
)

# ==========================================================
# File Upload Configuration
# ==========================================================

UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "data/uploads"
)

SAMPLE_DATA_FOLDER = os.getenv(
    "SAMPLE_DATA_FOLDER",
    "data/samples"
)

# ==========================================================
# Streamlit Configuration
# ==========================================================

STREAMLIT_TITLE = os.getenv(
    "STREAMLIT_TITLE",
    APP_NAME
)