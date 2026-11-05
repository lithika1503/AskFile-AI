"""PDF processing engine using pypdf."""

import io
from typing import List, Tuple
import pypdf
from utils.logging_config import logger
from utils.helpers import clean_extracted_text

class ScannedPDFError(Exception):
    """Raised when a PDF contains only scanned images and no selectable text."""
    pass

class PDFProcessor:
    """Extracts text page-by-page from PDF files."""

    @staticmethod
    def extract_pages(pdf_bytes: bytes) -> List[Tuple[int, str]]:
        """
        Extracts text from PDF bytes, returning a list of tuples: (page_number, page_text).
        Page numbers are 1-indexed.
        """
        pages_content: List[Tuple[int, str]] = []
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            total_extracted_chars = 0

            for page_idx, page in enumerate(reader.pages, start=1):
                try:
                    raw_text = page.extract_text() or ""
                    cleaned = clean_extracted_text(raw_text)
                    if cleaned:
                        total_extracted_chars += len(cleaned)
                    pages_content.append((page_idx, cleaned))
                except Exception as page_err:
                    logger.warning(f"Failed to extract page {page_idx}: {page_err}")
                    pages_content.append((page_idx, ""))

            # Graceful detection of scanned PDFs
            if total_pages > 0 and total_extracted_chars < 20:
                raise ScannedPDFError(
                    f"PDF contains {total_pages} page(s) but less than 20 characters of selectable text. "
                    "This document appears to be scanned images or rasterized without an OCR text layer."
                )

            return pages_content

        except ScannedPDFError:
            raise
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise ValueError(f"Could not parse PDF file: {str(e)}")
