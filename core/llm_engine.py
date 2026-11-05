"""Modular LLM Engine supporting Ollama, OpenAI, Gemini, and Local Extractive Synthesis."""

import json
import re
import requests
from typing import List, Dict, Any, Optional
from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    DEFAULT_LLM_PROVIDER
)
from utils.logging_config import logger

class LLMEngine:
    """
    Unified LLM router with support for local Ollama, OpenAI, Gemini,
    and a reliable local zero-cost Extractive Synthesizer.
    """

    def __init__(self, provider: str = DEFAULT_LLM_PROVIDER):
        self.provider = provider.lower()

    def generate_response(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.2
    ) -> str:
        """Routes prompt to the configured LLM provider."""
        if self.provider == "ollama":
            return self._call_ollama(prompt, system_instruction, temperature)
        elif self.provider == "openai":
            return self._call_openai(prompt, system_instruction, temperature)
        elif self.provider == "gemini":
            return self._call_gemini(prompt, system_instruction, temperature)
        else:
            return self._extractive_synthesizer(prompt)

    def _call_ollama(self, prompt: str, system_instruction: str, temperature: float) -> str:
        """Calls local Ollama API."""
        url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system_instruction,
            "stream": False,
            "options": {"temperature": temperature}
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.warning(f"Ollama returned status {response.status_code}: {response.text}")
                return (
                    f"⚠️ Ollama model error ({response.status_code}). "
                    "Ensure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3.2`)."
                )
        except requests.exceptions.ConnectionError:
            logger.warning("Could not connect to Ollama. Falling back to local extractive synthesizer.")
            return (
                "⚠️ **Ollama connection failed:** Ollama is not running on `http://localhost:11434`.\n\n"
                "To use local LLM generation:\n"
                "1. Open Terminal and run: `ollama run llama3.2`\n"
                "2. Or switch Provider to 'Extractive (Built-in)' in **Settings**.\n\n"
                + self._extractive_synthesizer(prompt)
            )
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error communicating with Ollama: {str(e)}"

    def _call_openai(self, prompt: str, system_instruction: str, temperature: float) -> str:
        """Calls OpenAI Chat Completions API."""
        if not OPENAI_API_KEY:
            return "⚠️ OpenAI API key not configured. Set OPENAI_API_KEY in environment or switch provider in Settings."

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": temperature
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=45)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
            return f"OpenAI API Error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"OpenAI connection error: {str(e)}"

    def _call_gemini(self, prompt: str, system_instruction: str, temperature: float) -> str:
        """Calls Google Gemini API."""
        if not GEMINI_API_KEY:
            return "⚠️ Gemini API key not configured. Set GEMINI_API_KEY in environment or switch provider in Settings."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        contents = []
        if system_instruction:
            contents.append({"role": "user", "parts": [{"text": f"Instruction: {system_instruction}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature}
        }
        try:
            res = requests.post(url, json=payload, timeout=45)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return f"Gemini API Error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"Gemini connection error: {str(e)}"

    def _extractive_synthesizer(self, prompt: str) -> str:
        """
        Built-in zero-cost extractive synthesizer.
        When no external LLM API is available, this engine extracts, ranks,
        and structures relevant findings directly from the provided context passages.
        """
        # Parse context and question from RAG prompt
        context_match = re.search(r"--- CONTEXT START ---\n(.*?)\n--- CONTEXT END ---", prompt, re.DOTALL)
        question_match = re.search(r"QUESTION:\s*(.*?)$", prompt, re.DOTALL)

        if not context_match:
            return "Based on the provided document excerpts, no sufficient supporting information was found to answer this question."

        context = context_match.group(1).strip()
        question = question_match.group(1).strip() if question_match else ""

        if not context:
            return "The requested information could not be found in the uploaded documents."

        # Extract sentences from context
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", context) if len(s.strip()) > 15]
        q_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", question.lower()))

        scored_sentences = []
        for s in sentences:
            s_lower = s.lower()
            matches = sum(1 for w in q_words if w in s_lower)
            if matches > 0:
                scored_sentences.append((matches, s))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s for _, s in scored_sentences[:6]]

        if not top_sentences:
            # Fallback to key passages
            top_sentences = sentences[:4]

        formatted_bullets = "\n".join([f"• {s}" for s in top_sentences])

        return (
            f"**Answer (Extracted from Document Context):**\n\n"
            f"{formatted_bullets}\n\n"
            f"> *Note: Generated using AskFile AI's local extractive synthesis engine.*"
        )
