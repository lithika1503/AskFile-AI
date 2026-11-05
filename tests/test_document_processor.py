"""Tests for Document Processing Engine (PDF, DOCX, TXT, validation, and error states)."""

import io
import pytest
import docx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from core.document_processor import DocumentProcessor
from core.pdf_processor import ScannedPDFError
from utils.helpers import compute_file_hash
from utils.validators import validate_uploaded_file

def create_sample_pdf(text: str) -> bytes:
    """Generates a valid PDF with selectable text in-memory."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    return buf.getvalue()

def create_sample_docx(text: str) -> bytes:
    """Generates a valid DOCX document in-memory."""
    doc = docx.Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def test_txt_extraction():
    content = "AskFile AI is an intelligent document analysis and RAG system.\nIt extracts text and indexes vectors."
    file_bytes = content.encode("utf-8")
    result = DocumentProcessor.process_file("sample.txt", file_bytes)
    
    assert result.file_type == "txt"
    assert result.total_pages == 1
    assert result.word_count > 10
    assert "AskFile AI" in result.full_text

def test_pdf_extraction():
    pdf_text = "This is a verified test paragraph embedded inside a PDF document for unit testing."
    pdf_bytes = create_sample_pdf(pdf_text)
    result = DocumentProcessor.process_file("test.pdf", pdf_bytes)
    
    assert result.file_type == "pdf"
    assert result.total_pages == 1
    assert "verified test paragraph" in result.full_text

def test_docx_extraction():
    docx_text = "Microsoft Word DOCX extraction unit test validating paragraph and table content."
    docx_bytes = create_sample_docx(docx_text)
    result = DocumentProcessor.process_file("document.docx", docx_bytes)
    
    assert result.file_type == "docx"
    assert "Microsoft Word DOCX" in result.full_text

def test_empty_document_handling():
    empty_bytes = b"   \n\t   "
    with pytest.raises(ValueError) as exc:
        DocumentProcessor.process_file("empty.txt", empty_bytes)
    assert "empty" in str(exc.value).lower()

def test_invalid_extension():
    with pytest.raises(ValueError) as exc:
        DocumentProcessor.process_file("malicious.exe", b"binary content")
    assert "unsupported" in str(exc.value).lower()

def test_file_validation():
    # Empty bytes
    valid, msg = validate_uploaded_file("doc.txt", 0, b"")
    assert valid is False
    
    # Exceeding size limit
    large_size = 30 * 1024 * 1024
    valid, msg = validate_uploaded_file("large.pdf", large_size, b"data")
    assert valid is False
    assert "exceeds" in msg.lower()

def test_duplicate_hash_computation():
    content_a = b"Consistent document text"
    content_b = b"Consistent document text"
    content_c = b"Different document text"
    
    hash_a = compute_file_hash(content_a)
    hash_b = compute_file_hash(content_b)
    hash_c = compute_file_hash(content_c)
    
    assert hash_a == hash_b
    assert hash_a != hash_c
