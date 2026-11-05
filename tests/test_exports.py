"""Tests for Export Service (PDF, DOCX, TXT, CSV, XLSX, JSON)."""

import pytest
import json
import io
import docx
import pypdf
import pandas as pd
from services.export_service import ExportService

def test_summary_exports():
    summary_data = {
        "summary": "This is a comprehensive document summary outlining critical deliverables.",
        "mode": "executive",
        "word_count": 12,
        "key_topics": ["Governance", "Architecture", "Validation"],
        "dates_and_figures": ["Date: 2024-10-15", "Financial: $100,000"]
    }
    
    # 1. TXT Export
    txt_bytes = ExportService.export_summary_txt("report.pdf", summary_data)
    assert len(txt_bytes) > 0
    assert "DOCUMENT ANALYSIS SUMMARY" in txt_bytes.decode("utf-8")
    
    # 2. DOCX Export
    docx_bytes = ExportService.export_summary_docx("report.pdf", summary_data)
    assert len(docx_bytes) > 0
    doc_in = docx.Document(io.BytesIO(docx_bytes))
    full_text = " ".join([p.text for p in doc_in.paragraphs])
    assert "Executive Summary" in full_text
    
    # 3. PDF Export
    pdf_bytes = ExportService.export_summary_pdf("report.pdf", summary_data)
    assert len(pdf_bytes) > 0
    pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(pdf_reader.pages) >= 1

def test_chat_exports():
    messages = [
        {"role": "user", "content": "What is the project milestone?", "created_at": "2024-11-01 10:00:00"},
        {"role": "assistant", "content": "The milestone is Q4 completion.", "created_at": "2024-11-01 10:00:05", "citations": [{"filename": "plan.pdf", "page_number": 2}]}
    ]
    txt_bytes = ExportService.export_chat_txt(messages, "Test Chat")
    assert "What is the project milestone?" in txt_bytes.decode("utf-8")
    
    pdf_bytes = ExportService.export_chat_pdf(messages, "Test Chat")
    assert len(pdf_bytes) > 0

def test_extraction_exports():
    data = {
        "emails": ["lead@example.com"],
        "phones": ["+1-555-0199"],
        "financials": ["$450,000"],
        "dates": ["November 2024"],
        "organizations": ["Acme Corp"],
        "person_names": ["Dr. Smith"],
        "headings": ["1. Executive Summary"],
        "objectives": ["Deliver scalable RAG pipeline"],
        "conclusions": ["System passes all performance metrics"],
        "action_items": ["Deploy on production host"],
        "key_terms": ["pipeline", "system"]
    }
    
    # JSON
    json_bytes = ExportService.export_extraction_json(data)
    parsed = json.loads(json_bytes.decode("utf-8"))
    assert parsed["emails"] == ["lead@example.com"]
    
    # CSV
    csv_bytes = ExportService.export_extraction_csv(data)
    df_csv = pd.read_csv(io.BytesIO(csv_bytes))
    assert len(df_csv) > 0
    assert "Category" in df_csv.columns
    
    # XLSX
    xlsx_bytes = ExportService.export_extraction_xlsx(data)
    df_xlsx = pd.read_excel(io.BytesIO(xlsx_bytes), engine="openpyxl")
    assert len(df_xlsx) > 0
