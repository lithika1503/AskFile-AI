"""Validation utilities for file uploads and user input."""

import os
from typing import Tuple, Optional
from config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS
from utils.constants import (
    ERR_FILE_TOO_LARGE,
    ERR_UNSUPPORTED_TYPE,
    ERR_EMPTY_FILE
)

def validate_uploaded_file(filename: str, file_size: int, content_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validates uploaded file against size, extension, and content rules.
    Returns (is_valid, error_message).
    """
    if not filename:
        return False, "File name cannot be empty."

    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        return False, ERR_UNSUPPORTED_TYPE.format(ext=ext)

    if file_size > MAX_FILE_SIZE_BYTES:
        return False, ERR_FILE_TOO_LARGE.format(max_size=MAX_FILE_SIZE_MB)

    if file_size == 0 or len(content_bytes) == 0:
        return False, ERR_EMPTY_FILE

    return True, None

def validate_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validates user query input."""
    if not query or not query.strip():
        return False, "Query cannot be empty."
    if len(query.strip()) < 2:
        return False, "Query is too short."
    if len(query) > 2000:
        return False, "Query exceeds maximum allowed length of 2000 characters."
    return True, None
