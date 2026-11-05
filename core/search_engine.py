"""Semantic search engine leveraging FAISS embeddings with query term highlighting."""

import re
from typing import List, Dict, Any, Optional
from core.embedding_engine import EmbeddingEngine
from core.vector_store import VectorStore
from utils.logging_config import logger

class SearchEngine:
    """Performs semantic similarity retrieval and keyword highlighting on document chunks."""

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        vector_store: Optional[VectorStore] = None
    ):
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.vector_store = vector_store or VectorStore(self.embedding_engine.get_dimension())

    def search(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
        min_score: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic search across document chunks.
        Returns ranked results with highlighted excerpts and similarity scores.
        """
        logger.info(f"Executing semantic search for '{query}'")
        query_vec = self.embedding_engine.embed_query(query)

        raw_results = self.vector_store.search(
            query_embedding=query_vec,
            top_k=top_k,
            document_ids=document_ids
        )

        # Extract search query tokens for highlighting
        query_tokens = [
            re.escape(token.lower())
            for token in re.findall(r"\b\w{3,}\b", query)
        ]

        formatted_results: List[Dict[str, Any]] = []
        for r in raw_results:
            score = r.get("score", 0.0)
            if score < min_score:
                continue

            text = r.get("chunk_text", "")
            highlighted = self._highlight_text(text, query_tokens)

            formatted_results.append({
                "document_id": r["document_id"],
                "filename": r.get("filename", ""),
                "page_number": r.get("page_number", 1),
                "chunk_index": r.get("chunk_index", 0),
                "score": score,
                "relevance_percentage": int(score * 100),
                "raw_text": text,
                "highlighted_html": highlighted
            })

        return formatted_results

    def _highlight_text(self, text: str, query_tokens: List[str]) -> str:
        """Surrounds matched keywords with HTML mark tags."""
        if not query_tokens:
            return text

        pattern = re.compile(r"\b(" + "|".join(query_tokens) + r")\b", re.IGNORECASE)
        return pattern.sub(r"<mark style='background-color: #3B82F6; color: #FFFFFF; padding: 2px 4px; border-radius: 3px;'>\1</mark>", text)
