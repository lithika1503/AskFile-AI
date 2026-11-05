"""
Module 12: Settings & System Configuration
Configure chunking parameters, vector embeddings, LLM inference endpoints, and storage management.
"""

import streamlit as st
import os
from config import (
    APP_NAME,
    APP_VERSION,
    DATABASE_PATH,
    STORAGE_DIR,
    UPLOADS_DIR,
    VECTOR_DB_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_TOP_K,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL
)
from database.repository import AnalyticsRepository
from utils.helpers import format_file_size
from utils.ui import apply_custom_theme, render_header, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Settings", page_icon="⚙️", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Application Settings", "Fine-tune RAG chunking parameters, embedding models, and inference backends")

# -------------------------------------------------------------
# Section 1: RAG & Chunking Parameters
# -------------------------------------------------------------
st.markdown("### 🧩 RAG & Vector Search Configuration")

col1, col2, col3 = st.columns(3)
with col1:
    chunk_size = st.slider(
        "Chunk Size (Characters):",
        min_value=200,
        max_value=2000,
        value=st.session_state.get("cfg_chunk_size", DEFAULT_CHUNK_SIZE),
        step=50,
        help="Target length of each document segment."
    )
    st.session_state["cfg_chunk_size"] = chunk_size

with col2:
    chunk_overlap = st.slider(
        "Chunk Overlap (Characters):",
        min_value=20,
        max_value=400,
        value=st.session_state.get("cfg_chunk_overlap", DEFAULT_CHUNK_OVERLAP),
        step=20,
        help="Characters preserved across chunk boundaries to preserve semantic context."
    )
    st.session_state["cfg_chunk_overlap"] = chunk_overlap

with col3:
    top_k = st.slider(
        "Retrieval Top-K (Passages):",
        min_value=1,
        max_value=12,
        value=st.session_state.get("cfg_top_k", DEFAULT_TOP_K),
        step=1,
        help="Number of most similar passages retrieved by FAISS for query synthesis."
    )
    st.session_state["cfg_top_k"] = top_k

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Section 2: AI & LLM Inference Backend
# -------------------------------------------------------------
st.markdown("### 🤖 LLM & Embedding Engine")

p_col1, p_col2 = st.columns(2)
with p_col1:
    embedding_model = st.selectbox(
        "Sentence Transformer Embedding Model:",
        options=[
            "all-MiniLM-L6-v2 (Fast CPU Default, 384-dim)",
            "paraphrase-MiniLM-L3-v2 (Ultra Lightweight)",
            "all-mpnet-base-v2 (High Precision, 768-dim)"
        ],
        index=0,
        help="Locally running embedding model used for vector representations in FAISS."
    )

with p_col2:
    provider = st.selectbox(
        "Language Model Provider:",
        options=[
            "Extractive (Zero-Cost Built-In Synthesizer)",
            "Ollama (Local LLM Inference)",
            "OpenAI API (Cloud)",
            "Google Gemini API (Cloud)"
        ],
        index=0 if DEFAULT_LLM_PROVIDER == "extractive" else 1
    )

# Provider Specific Guidance
clean_provider = provider.split()[0].lower()
if clean_provider == "ollama":
    st.markdown(
        """
        <div class="askfile-card" style="border-left: 3px solid #10B981;">
            <b>Ollama Local Configuration:</b><br>
            Endpoint: <code>http://localhost:11434</code><br>
            Model: <code>llama3.2</code> (or <code>mistral</code>)<br>
            <i>Ensure Ollama is started locally via: <code>ollama run llama3.2</code> in your terminal.</i>
        </div>
        """,
        unsafe_allow_html=True
    )
elif clean_provider == "openai":
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    status_text = "✅ Configured via environment" if has_key else "⚠️ OPENAI_API_KEY environment variable not detected"
    st.info(f"OpenAI Backend: {status_text}. Secrets are securely read from the environment.")
elif clean_provider == "google":
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    status_text = "✅ Configured via environment" if has_key else "⚠️ GEMINI_API_KEY environment variable not detected"
    st.info(f"Gemini Backend: {status_text}. Secrets are securely read from the environment.")
else:
    st.success("✅ **Extractive Built-In Mode:** Runs completely offline without external servers or API keys. Generates factual answers directly synthesized from retrieved document context.")

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Section 3: Storage & System Maintenance
# -------------------------------------------------------------
st.markdown("### 💾 Storage & Data Management")

# Compute storage stats
upload_files = list(UPLOADS_DIR.glob("*"))
total_upload_size = sum(f.stat().st_size for f in upload_files)
db_size = DATABASE_PATH.stat().st_size if DATABASE_PATH.exists() else 0
vector_files = list(VECTOR_DB_DIR.glob("*"))
vector_size = sum(f.stat().st_size for f in vector_files)

s1, s2, s3 = st.columns(3)
with s1:
    st.metric("Database Size (SQLite)", format_file_size(db_size))
with s2:
    st.metric("Uploaded Files Storage", format_file_size(total_upload_size), f"{len(upload_files)} files")
with s3:
    st.metric("FAISS Index Storage", format_file_size(vector_size), f"{len(vector_files)} artifacts")

st.markdown("---")
st.markdown("##### ⚠️ Danger Zone")
if st.button("🗑️ Purge All Chat Messages and Activity Logs", type="secondary"):
    AnalyticsRepository.clear_all_history()
    st.success("Chat conversations, messages, and activity audit trails have been purged.")
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.caption(f"{APP_NAME} v{APP_VERSION} • Developed with Streamlit, FAISS, Sentence Transformers & SQLite.")
