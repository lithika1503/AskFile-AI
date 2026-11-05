"""DOCX processing engine using python-docx."""

import io
from typing import List, Tuple
import docx
from utils.logging_config import logger
from utils.helpers import clean_extracted_text

class DOCXProcessor:
    """Extracts text from DOCX files including paragraphs and tables."""

    @staticmethod
    def extract_pages(docx_bytes: bytes) -> List[Tuple[int, str]]:
        """
        Extracts structured text from a DOCX file.
        DOCX is a flow format without rigid page breaks, so content is grouped into logical sections.
        Returns a list of (page_or_section_number, text).
        """
        try:
            doc = docx.Document(io.BytesIO(docx_bytes))
            sections_text: List[str] = []

            # Extract paragraphs
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    sections_text.append(text)

            # Extract tables
            for table in doc.tables:
                table_rows = []
                for row in table.rows:
                    row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if row_cells:
                        table_rows.append(" | ".join(row_cells))
                if table_rows:
                    sections_text.append("\n".join(table_rows))

            full_text = "\n\n".join(sections_text)
            cleaned = clean_extracted_text(full_text)

            if not cleaned:
                raise ValueError("DOCX document contains no readable text.")

            # In DOCX, return as page 1 or split by explicit section if large
            return [(1, cleaned)]

        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
            raise ValueError(f"Could not parse DOCX file: {str(e)}")
