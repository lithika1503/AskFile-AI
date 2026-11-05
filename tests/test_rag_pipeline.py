"""Tests for Text Chunking, Embeddings, FAISS Vector Store, and RAG Pipeline."""

import pytest
import numpy as np
from core.text_chunker import TextChunker
from core.embedding_engine import EmbeddingEngine
from core.vector_store import VectorStore
from core.llm_engine import LLMEngine
from core.rag_pipeline import RAGPipeline
from database.models import DocumentChunk

def test_text_chunking():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    pages = [
        (1, "First page sentence one. First page sentence two. First page sentence three."),
        (2, "Second page introductory text with additional explanatory content.")
    ]
    chunks = chunker.chunk_document("doc-123", pages)
    
    assert len(chunks) > 1
    assert all(c.document_id == "doc-123" for c in chunks)
    assert chunks[0].page_number == 1
    assert chunks[-1].page_number == 2
    assert chunks[0].chunk_index == 0

def test_embeddings_and_vector_store():
    embedding_engine = EmbeddingEngine()
    dim = embedding_engine.get_dimension()
    assert dim > 0
    
    # Test batch embedding
    texts = [
        "Artificial Intelligence in Healthcare diagnostics and imaging.",
        "Deep Learning neural network backpropagation algorithms.",
        "Financial forecasting and quarterly revenue analysis."
    ]
    embeddings = embedding_engine.embed_texts(texts)
    assert embeddings.shape == (3, dim)
    
    # Test FAISS vector indexing
    v_store = VectorStore(dimension=dim)
    v_store.reset()
    
    chunk1 = DocumentChunk("doc_ai", 0, texts[0], 1, "ref1")
    chunk2 = DocumentChunk("doc_ai", 1, texts[1], 1, "ref2")
    chunk3 = DocumentChunk("doc_fin", 0, texts[2], 1, "ref3")
    
    v_store.add_chunks([chunk1, chunk2, chunk3], embeddings, filename="test_corpus")
    
    # Test similarity retrieval
    q_vec = embedding_engine.embed_query("medical diagnosis and health patient data")
    results = v_store.search(q_vec, top_k=2)
    assert len(results) >= 1
    assert results[0]["document_id"] == "doc_ai"
    assert "Healthcare" in results[0]["chunk_text"]
    
    # Test Document Filtering (prevents cross-contamination)
    filtered_results = v_store.search(q_vec, top_k=2, document_ids=["doc_fin"])
    assert len(filtered_results) == 1
    assert filtered_results[0]["document_id"] == "doc_fin"
    assert "Financial" in filtered_results[0]["chunk_text"]

def test_rag_with_mock_llm(monkeypatch):
    embedding_engine = EmbeddingEngine()
    v_store = VectorStore(dimension=embedding_engine.get_dimension())
    v_store.reset()
    
    passage = "Project Alpha was officially launched on October 15, 2024 with a budget of $500,000."
    vec = embedding_engine.embed_texts([passage])
    chunk = DocumentChunk("doc_proj", 0, passage, 1, "proj_0")
    v_store.add_chunks([chunk], vec, filename="project_charter.pdf")
    
    # Mock LLM to verify prompt passing and source citations
    class MockLLMEngine(LLMEngine):
        def generate_response(self, prompt: str, system_instruction: str = "", temperature: float = 0.2) -> str:
            assert "--- CONTEXT START ---" in prompt
            assert "October 15, 2024" in prompt
            return "Project Alpha launched on October 15, 2024 with a $500,000 budget."
            
    mock_llm = MockLLMEngine(provider="mock")
    pipeline = RAGPipeline(
        embedding_engine=embedding_engine,
        vector_store=v_store,
        llm_engine=mock_llm,
        top_k=1
    )
    
    res = pipeline.answer_question("When was Project Alpha launched?", document_ids=["doc_proj"])
    assert "October 15, 2024" in res["answer"]
    assert len(res["citations"]) == 1
    assert res["citations"][0]["filename"] == "project_charter.pdf"
    assert res["citations"][0]["page_number"] == 1
