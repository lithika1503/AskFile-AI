"""
Configuration settings for AskFile AI.
Handles paths, model choices, RAG parameters, and environment variables.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
VECTOR_DB_DIR = STORAGE_DIR / "vector_db"
DATABASE_PATH = STORAGE_DIR / "askfile.db"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure runtime directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Application Metadata
APP_NAME = "AskFile AI"
APP_SUBTITLE = "Intelligent Document Analysis & Question Answering System"
APP_VERSION = "1.0.0"

# File Processing Constraints
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 25))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt"]

# RAG & Chunking Defaults
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", 500))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", 100))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 4))

# Embedding Engine Defaults
# all-MiniLM-L6-v2 is compact (80MB), fast, and performs exceptionally on CPU
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # for all-MiniLM-L6-v2

# LLM Configuration
# Providers: 'ollama', 'openai', 'gemini', 'extractive'
DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "extractive")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# UI Palette - Premium Dark Navy Theme
UI_THEME = {
    "primary": "#3B82F6",       # Bright Electric Blue
    "secondary": "#1E40AF",     # Deep Navy
    "background": "#0B1120",    # Rich Dark Slate Navy
    "card_bg": "#1E293B",       # Slate 800 Card
    "card_border": "#334155",   # Slate 700 Border
    "text": "#F8FAFC",          # Slate 50
    "text_muted": "#94A3B8",    # Slate 400
    "success": "#10B981",       # Emerald 500
    "warning": "#F59E0B",       # Amber 500
    "danger": "#EF4444",        # Rose 500
}
