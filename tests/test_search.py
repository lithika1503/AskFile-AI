"""Tests for Semantic Search Engine."""

import pytest
from core.embedding_engine import EmbeddingEngine
from core.vector_store import VectorStore
from core.search_engine import SearchEngine
from database.models import DocumentChunk

def test_semantic_search_and_highlighting():
    embedding_engine = EmbeddingEngine()
    v_store = VectorStore(dimension=embedding_engine.get_dimension())
    v_store.reset()
    
    text = "The machine learning algorithm optimizes cross entropy loss over five epochs."
    vec = embedding_engine.embed_texts([text])
    chunk = DocumentChunk("doc_ml", 0, text, 1, "ml_0")
    v_store.add_chunks([chunk], vec, filename="ml_guide.txt")
    
    search_engine = SearchEngine(embedding_engine=embedding_engine, vector_store=v_store)
    
    # Query with semantic variation
    results = search_engine.search("deep neural model cost minimization", top_k=1)
    assert len(results) == 1
    assert results[0]["filename"] == "ml_guide.txt"
    assert results[0]["score"] > 0
    assert "relevance_percentage" in results[0]
    
    # Verify keyword highlighting
    results_highlight = search_engine.search("machine learning algorithm", top_k=1)
    assert "<mark" in results_highlight[0]["highlighted_html"]
