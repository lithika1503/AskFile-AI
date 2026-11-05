"""Document Comparison Engine computing embedding cosine similarity and thematic contrast."""

import re
from typing import Dict, Any, List, Optional, Set
import numpy as np
from core.embedding_engine import EmbeddingEngine
from core.llm_engine import LLMEngine
from utils.logging_config import logger

class DocumentComparisonEngine:
    """Compares two documents using vector embeddings and semantic difference analysis."""

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        llm_engine: Optional[LLMEngine] = None
    ):
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.llm_engine = llm_engine or LLMEngine()

    def compare(
        self,
        doc_a_name: str,
        doc_a_text: str,
        doc_b_name: str,
        doc_b_text: str
    ) -> Dict[str, Any]:
        """
        Calculates semantic similarity, common and unique topics,
        and generates a comparative synthesis.
        """
        logger.info(f"Comparing '{doc_a_name}' vs '{doc_b_name}'")

        # 1. Compute embedding cosine similarity
        vec_a = self.embedding_engine.embed_query(doc_a_text[:4000])
        vec_b = self.embedding_engine.embed_query(doc_b_text[:4000])

        # Cosine similarity between unit normalized vectors
        cosine_sim = float(np.dot(vec_a, vec_b))
        similarity_pct = round(max(0.0, min(1.0, cosine_sim)) * 100, 1)

        # 2. Topic and vocabulary overlap
        tokens_a = self._tokenize(doc_a_text)
        tokens_b = self._tokenize(doc_b_text)

        common_topics = sorted(list(tokens_a.intersection(tokens_b)))[:15]
        unique_to_a = sorted(list(tokens_a - tokens_b))[:15]
        unique_to_b = sorted(list(tokens_b - tokens_a))[:15]

        # Jaccard lexical similarity
        union_len = len(tokens_a.union(tokens_b))
        jaccard_sim = round((len(common_topics) / max(1, union_len)) * 100, 1)

        # 3. Structural comparison
        headings_a = self._extract_headings(doc_a_text)
        headings_b = self._extract_headings(doc_b_text)
        missing_in_b = [h for h in headings_a if h.lower() not in [x.lower() for x in headings_b]][:6]
        missing_in_a = [h for h in headings_b if h.lower() not in [x.lower() for x in headings_a]][:6]

        # 4. Generate AI comparison narrative
        ai_summary = self._generate_comparison_summary(
            doc_a_name, doc_a_text,
            doc_b_name, doc_b_text,
            similarity_pct
        )

        return {
            "doc_a_name": doc_a_name,
            "doc_b_name": doc_b_name,
            "similarity_percentage": similarity_pct,
            "similarity_metric": "SentenceTransformer Embedding Cosine Similarity (all-MiniLM-L6-v2)",
            "jaccard_overlap_percentage": jaccard_sim,
            "common_topics": common_topics,
            "unique_to_doc_a": unique_to_a,
            "unique_to_doc_b": unique_to_b,
            "headings_doc_a": headings_a,
            "headings_doc_b": headings_b,
            "missing_in_doc_b": missing_in_b,
            "missing_in_doc_a": missing_in_a,
            "comparison_summary": ai_summary,
            "disclaimer": "Semantic similarity indicates thematic alignment of text embeddings. It is not an assessment of plagiarism or factual correctness."
        }

    def _tokenize(self, text: str) -> Set[str]:
        words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())
        stopwords = {
            "this", "that", "with", "from", "have", "were", "which", "there",
            "their", "about", "would", "these", "other", "could", "should",
            "document", "using", "between", "under", "after", "before"
        }
        return {w for w in words if w not in stopwords}

    def _extract_headings(self, text: str) -> List[str]:
        lines = text.split("\n")
        headings = []
        for line in lines:
            line_s = line.strip()
            if 3 < len(line_s) < 80 and (
                line_s.startswith("#") or
                re.match(r"^\d+\.\s+[A-Z]", line_s) or
                line_s.isupper()
            ):
                headings.append(line_s.lstrip("# ").strip())
        return headings[:10]

    def _generate_comparison_summary(
        self,
        name_a: str,
        text_a: str,
        name_b: str,
        text_b: str,
        sim_pct: float
    ) -> str:
        prompt = (
            f"Compare the contents of these two documents:\n\n"
            f"DOCUMENT A: '{name_a}'\n"
            f"Excerpts:\n{text_a[:2500]}\n\n"
            f"DOCUMENT B: '{name_b}'\n"
            f"Excerpts:\n{text_b[:2500]}\n\n"
            f"Observed Semantic Similarity: {sim_pct}%\n\n"
            f"Please provide:\n"
            f"1. Core Focus & Thematic Overlap\n"
            f"2. Major Differences and Unique Points\n"
            f"3. Key Conclusions of Document A vs Document B\n"
            f"Keep your analysis clear, professional, and structured in bullet points."
        )
        return self.llm_engine.generate_response(prompt)
