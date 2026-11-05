"""Tests for Summarization and Document Comparison Engines."""

import pytest
from core.summarizer import DocumentSummarizer
from core.comparison_engine import DocumentComparisonEngine
from core.llm_engine import LLMEngine

def test_document_summarizer():
    summarizer = DocumentSummarizer(llm_engine=LLMEngine(provider="extractive"))
    text = (
        "The AskFile AI initiative commenced in January 2024. "
        "The project achieved a 95% accuracy rate with a budget allocation of $250,000. "
        "Key stakeholders confirmed the deliverables met all performance specifications. "
        "Final rollout is scheduled for December 15, 2024."
    )
    
    res = summarizer.summarize(text, filename="status_report.txt", mode="short")
    assert "summary" in res
    assert len(res["summary"]) > 0
    assert any("2024" in item for item in res["dates_and_figures"])
    assert any("250,000" in item for item in res["dates_and_figures"])

def test_document_comparison():
    engine = DocumentComparisonEngine(llm_engine=LLMEngine(provider="extractive"))
    
    doc_a = (
        "# Introduction to Renewable Energy\n"
        "Solar photovoltaic systems convert sunlight into electrical power.\n"
        "Battery storage units ensure grid stability during peak consumption."
    )
    doc_b = (
        "# Overview of Solar Power Systems\n"
        "Solar photovoltaic panels generate direct current electricity from solar radiation.\n"
        "Modern energy inverters provide reliable utility distribution."
    )
    
    comparison = engine.compare("solar_a.txt", doc_a, "solar_b.txt", doc_b)
    
    assert comparison["similarity_percentage"] > 50.0
    assert "solar" in [t.lower() for t in comparison["common_topics"]]
    assert "disclaimer" in comparison
    assert len(comparison["comparison_summary"]) > 0
