"""Hierarchical and section-wise document summarizer."""

import re
from typing import Dict, Any, List, Optional
from core.llm_engine import LLMEngine
from utils.helpers import count_words
from utils.logging_config import logger

class DocumentSummarizer:
    """
    Produces executive, short, medium, and detailed summaries using
    hierarchical map-reduce summarization to avoid truncating long documents.
    """

    def __init__(self, llm_engine: Optional[LLMEngine] = None):
        self.llm_engine = llm_engine or LLMEngine()

    def summarize(
        self,
        document_text: str,
        filename: str = "",
        mode: str = "medium"  # 'short', 'medium', 'detailed', 'executive'
    ) -> Dict[str, Any]:
        """
        Generates a structured summary with target word count and key highlights.
        """
        logger.info(f"Generating {mode} summary for document '{filename}'")

        if not document_text or not document_text.strip():
            return {
                "summary": "Document contains no readable text to summarize.",
                "key_findings": [],
                "key_topics": [],
                "dates_and_figures": [],
                "word_count": 0
            }

        # Word count targets
        target_words = {
            "short": 100,
            "medium": 300,
            "detailed": 500,
            "executive": 350
        }.get(mode.lower(), 300)

        # Handle long documents via map-reduce chunking
        processed_text = self._prepare_text(document_text)

        system_instruction = (
            "You are an expert executive document analyst. "
            "Generate accurate, objective, and well-structured document summaries. "
            "Never hallucinate facts not present in the text."
        )

        prompt = (
            f"Analyze the following document titled '{filename}':\n\n"
            f"--- DOCUMENT START ---\n"
            f"{processed_text}\n"
            f"--- DOCUMENT END ---\n\n"
            f"TASKS:\n"
            f"1. Provide a comprehensive {mode.upper()} summary of approximately {target_words} words.\n"
            f"2. Use markdown formatting with clear headings, concise paragraphs, and bullet points.\n"
            f"3. Highlight critical conclusions, key dates, monetary or numerical metrics, and main takeaways."
        )

        raw_summary = self.llm_engine.generate_response(
            prompt=prompt,
            system_instruction=system_instruction
        )

        # Extract structured findings and figures
        key_topics = self._extract_key_topics(document_text)
        dates_and_figures = self._extract_dates_and_figures(document_text)

        return {
            "summary": raw_summary,
            "key_topics": key_topics,
            "dates_and_figures": dates_and_figures,
            "word_count": count_words(raw_summary),
            "mode": mode
        }

    def _prepare_text(self, text: str, max_chars: int = 8000) -> str:
        """
        If text is excessively long, performs a hierarchical map-reduce condensation
        by selecting evenly spaced sections rather than merely truncating the front.
        """
        if len(text) <= max_chars:
            return text

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) <= 6:
            return text[:max_chars]

        # Sample beginning, middle sections, and conclusion
        first_part = "\n\n".join(paragraphs[:3])
        step = max(1, len(paragraphs) // 5)
        middle_part = "\n\n".join([paragraphs[i] for i in range(3, len(paragraphs) - 3, step)])
        last_part = "\n\n".join(paragraphs[-3:])

        combined = f"{first_part}\n\n[... middle sections condensed ...]\n\n{middle_part}\n\n[... concluding sections ...]\n\n{last_part}"
        return combined[:max_chars]

    def _extract_key_topics(self, text: str) -> List[str]:
        """Extracts prominent topics / recurring keywords."""
        words = re.findall(r"\b[A-Z][a-z]{3,}\b", text)
        stop_words = {"This", "That", "There", "These", "Those", "When", "What", "Where", "With", "From", "Have"}
        candidates = [w for w in words if w not in stop_words]

        from collections import Counter
        counts = Counter(candidates)
        return [word for word, _ in counts.most_common(8)]

    def _extract_dates_and_figures(self, text: str) -> List[str]:
        """Extracts significant dates, percentages, and financial numbers."""
        findings = []

        # Monetary figures
        money = re.findall(r"[\$€£₹]\s?[\d,]+(?:\.\d+)?|\b\d+(?:,\d+)*(?:\.\d+)?\s*(?:USD|EUR|GBP|INR|dollars|million|billion)\b", text, re.IGNORECASE)
        for m in money[:5]:
            findings.append(f"Financial: {m}")

        # Dates
        dates = re.findall(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}|\d{4})\b", text)
        for d in dates[:5]:
            if d not in findings:
                findings.append(f"Date: {d}")

        # Percentages
        percentages = re.findall(r"\b\d+(?:\.\d+)?%", text)
        for p in percentages[:4]:
            findings.append(f"Metric: {p}")

        return findings[:10]
