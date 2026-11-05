"""Helper functions for text cleaning, formatting, word counts, and hashes."""

import hashlib
import re
import unicodedata
from datetime import datetime
from typing import Optional

def compute_file_hash(file_bytes: bytes) -> str:
    """Computes SHA-256 hash of file content."""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()

def clean_extracted_text(text: str) -> str:
    """
    Cleans raw extracted text:
    - Normalizes unicode characters
    - Fixes hyphenated line-breaks
    - Replaces excessive newlines and whitespace
    - Removes non-printable null bytes
    """
    if not text:
        return ""
    # Remove null bytes
    text = text.replace("\x00", "")
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Fix hyphenated words broken across lines
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple consecutive newlines (more than 2) to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse inline spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def count_words(text: str) -> int:
    """Returns the total number of words in a text string."""
    if not text:
        return 0
    return len(re.findall(r"\b\w+\b", text))

def format_file_size(size_bytes: int) -> str:
    """Formats bytes into human-readable format (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def sanitize_filename(filename: str) -> str:
    """Sanitizes file name to prevent path traversal and shell injection."""
    filename = Path_clean = re.sub(r"[^\w\s\.-]", "_", filename)
    filename = filename.strip(". ")
    return filename or "document"

def format_timestamp(ts_str: Optional[str]) -> str:
    """Formats an ISO or SQLite timestamp into a readable string."""
    if not ts_str:
        return ""
    try:
        # SQLite timestamps are typically 'YYYY-MM-DD HH:MM:SS'
        dt = datetime.fromisoformat(ts_str.replace(" ", "T"))
        return dt.strftime("%b %d, %Y - %I:%M %p")
    except Exception:
        return str(ts_str)
