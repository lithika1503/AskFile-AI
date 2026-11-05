"""Structured Information Extraction Engine using regex patterns and heuristic NLP."""

import re
from typing import Dict, List, Any

class InformationExtractor:
    """
    Extracts structured entities, contact details, financial numbers,
    action items, and objectives from document text.
    """

    @staticmethod
    def extract_all(text: str) -> Dict[str, Any]:
        """Runs all information extraction routines on text."""
        if not text:
            return {}

        emails = InformationExtractor.extract_emails(text)
        phones = InformationExtractor.extract_phone_numbers(text)
        financials = InformationExtractor.extract_financials(text)
        dates = InformationExtractor.extract_dates(text)
        orgs = InformationExtractor.extract_organizations(text)
        names = InformationExtractor.extract_names(text)
        headings = InformationExtractor.extract_headings(text)
        objectives = InformationExtractor.extract_objectives(text)
        conclusions = InformationExtractor.extract_conclusions(text)
        action_items = InformationExtractor.extract_action_items(text)
        key_terms = InformationExtractor.extract_key_terms(text)

        return {
            "emails": emails,
            "phones": phones,
            "financials": financials,
            "dates": dates,
            "organizations": orgs,
            "person_names": names,
            "headings": headings,
            "objectives": objectives,
            "conclusions": conclusions,
            "action_items": action_items,
            "key_terms": key_terms,
            "total_entities_found": (
                len(emails) + len(phones) + len(financials) + len(dates) +
                len(orgs) + len(names) + len(action_items)
            )
        }

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        return sorted(list(set(re.findall(pattern, text))))

    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        # International and domestic phone formats
        pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        matches = re.findall(pattern, text)
        cleaned = [m.strip() for m in matches if len(re.sub(r"\D", "", m)) >= 10]
        return sorted(list(set(cleaned)))

    @staticmethod
    def extract_financials(text: str) -> List[str]:
        pattern = r"[\$€£₹]\s?[\d,]+(?:\.\d+)?(?:\s?(?:million|billion|trillion|k|m|b))?|\b\d+(?:,\d+)*(?:\.\d+)?\s*(?:USD|EUR|GBP|INR|dollars|cents)\b"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return sorted(list(set([m.strip() for m in matches])))

    @staticmethod
    def extract_dates(text: str) -> List[str]:
        patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
            r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b",
            r"\b(?:Q[1-4]|Quarter [1-4])\s*(?:20\d\d|\d\d)\b"
        ]
        results = set()
        for p in patterns:
            for m in re.findall(p, text, re.IGNORECASE):
                results.add(m.strip())
        return sorted(list(results))

    @staticmethod
    def extract_organizations(text: str) -> List[str]:
        # Common corporate designators
        pattern = r"\b[A-Z][A-Za-z0-9&\s]{1,30}\s+(?:Inc\.?|Corp\.?|Corporation|LLC|Ltd\.?|Limited|Group|Technologies|Solutions|University|Bank|Foundation)\b"
        matches = re.findall(pattern, text)
        return sorted(list(set([m.strip() for m in matches])))[:15]

    @staticmethod
    def extract_names(text: str) -> List[str]:
        # Titles followed by Capitalized names
        pattern = r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Director|Officer|Manager)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+))\b"
        matches = re.findall(pattern, text)
        return sorted(list(set(matches)))[:15]

    @staticmethod
    def extract_headings(text: str) -> List[str]:
        # Numbered headings, markdown headers, or uppercase lines
        lines = text.split("\n")
        headings = []
        for line in lines:
            line_s = line.strip()
            if not line_s or len(line_s) > 100:
                continue
            if re.match(r"^(?:#+|\d+\.\d*|[A-Z\s]{4,}|Chapter|Section)\b", line_s):
                headings.append(line_s.lstrip("#").strip())
        return headings[:15]

    @staticmethod
    def extract_objectives(text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        matches = []
        keywords = ["objective", "goal", "purpose", "aim", "target", "mission", "scope of"]
        for s in sentences:
            s_clean = s.strip()
            if any(k in s_clean.lower() for k in keywords) and 20 < len(s_clean) < 300:
                matches.append(s_clean)
        return matches[:8]

    @staticmethod
    def extract_conclusions(text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        matches = []
        keywords = ["conclude", "conclusion", "in summary", "finally", "outcome", "result shows", "findings suggest"]
        for s in sentences:
            s_clean = s.strip()
            if any(k in s_clean.lower() for k in keywords) and 20 < len(s_clean) < 300:
                matches.append(s_clean)
        return matches[:8]

    @staticmethod
    def extract_action_items(text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        matches = []
        keywords = ["must", "shall", "action required", "next steps", "deliverable", "responsible for", "deadline"]
        for s in sentences:
            s_clean = s.strip()
            if any(k in s_clean.lower() for k in keywords) and 20 < len(s_clean) < 300:
                matches.append(s_clean)
        return matches[:8]

    @staticmethod
    def extract_key_terms(text: str) -> List[str]:
        words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())
        stopwords = {
            "this", "that", "with", "from", "have", "were", "which", "there",
            "their", "about", "would", "these", "other", "could", "should", "document"
        }
        filtered = [w for w in words if w not in stopwords]
        from collections import Counter
        counts = Counter(filtered)
        return [w for w, _ in counts.most_common(12)]
