"""Unified Document Processing Engine for PDF, DOCX, and TXT files."""

import os
from typing import List, Tuple, Dict, Any
from utils.constants import TYPE_PDF, TYPE_DOCX, TYPE_TXT
from utils.helpers import clean_extracted_text, count_words
from utils.logging_config import logger
from core.pdf_processor import PDFProcessor, ScannedPDFError
from core.docx_processor import DOCXProcessor

class DocumentProcessingResult:
    """Encapsulates the output of extracting a document."""
    def __init__(
        self,
        file_type: str,
        total_pages: int,
        word_count: int,
        full_text: str,
        pages_content: List[Tuple[int, str]],
        warning: str = ""
    ):
        self.file_type = file_type
        self.total_pages = total_pages
        self.word_count = word_count
        self.full_text = full_text
        self.pages_content = pages_content
        self.warning = warning

class DocumentProcessor:
    """Reusable engine for multi-format document extraction."""

    @staticmethod
    def process_file(filename: str, file_bytes: bytes) -> DocumentProcessingResult:
        """
        Processes an uploaded file based on its extension.
        Returns DocumentProcessingResult with structured text and page mapping.
        """
        _, ext = os.path.splitext(filename.lower())
        warning = ""

        if ext == ".pdf":
            file_type = TYPE_PDF
            try:
                pages_content = PDFProcessor.extract_pages(file_bytes)
            except ScannedPDFError as se:
                logger.warning(f"Scanned PDF detected in {filename}: {se}")
                raise ValueError(str(se))

        elif ext == ".docx":
            file_type = TYPE_DOCX
            pages_content = DOCXProcessor.extract_pages(file_bytes)

        elif ext == ".txt":
            file_type = TYPE_TXT
            try:
                # Attempt UTF-8 then fallback to latin-1
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="replace")
                warning = "Document contained non-UTF8 characters that were decoded with fallback encoding."

            cleaned = clean_extracted_text(text)
            if not cleaned:
                raise ValueError("TXT file is empty or contains only whitespace.")
            pages_content = [(1, cleaned)]

        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        # Assemble full text
        full_text = "\n\n".join([text for _, text in pages_content if text.strip()])
        word_cnt = count_words(full_text)
        total_pages = len(pages_content)

        if word_cnt == 0:
            raise ValueError(f"Document '{filename}' contains no readable text words.")

        return DocumentProcessingResult(
            file_type=file_type,
            total_pages=total_pages,
            word_count=word_cnt,
            full_text=full_text,
            pages_content=pages_content,
            warning=warning
        )
