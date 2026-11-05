# AskFile AI – Intelligent File Analysis & Question Answering System

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![Vector Index](https://img.shields.io/badge/FAISS-CPU%20Indexed-green.svg)](https://github.com/facebookresearch/faiss)
[![Embeddings](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-purple.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

**AskFile AI** is an enterprise-grade document intelligence and question-answering platform built with Python, Streamlit, and Retrieval-Augmented Generation (RAG). It transforms ordinary documents (PDF, DOCX, TXT) into structured, searchable, and interactive knowledge sources with verifiable citations.

---

## 🌟 Key Capabilities & Modules

1. **Dashboard & Analytics (Module 1 & 9)**
   - Real-time SQLite statistics: Total documents, word counts, questions asked, and processing health.
   - Interactive Plotly visualizations for format distribution, ingestion timelines, and activity breakdowns.

2. **Multi-Format Document Upload (Module 2)**
   - Drag-and-drop ingestion supporting `.pdf`, `.docx`, and `.txt` up to 25 MB.
   - SHA-256 cryptographic deduplication preventing duplicate ingestion.
   - Page preservation, word counts, text preview, reprocessing, and cascading deletions.

3. **Core RAG & AI Chatbot (Module 5)**
   - Source-grounded conversational QA preventing hallucinations.
   - Inspectable source evidence cards with exact file names, page numbers, and cosine relevance scores.
   - Multi-document target filtering to prevent cross-document contamination.
   - Multi-turn conversation history and downloadable transcripts in PDF and TXT.

4. **Hierarchical Document Summarizer (Module 4)**
   - Multi-tier summarization: **Executive**, **Short (~100 words)**, **Medium (~300 words)**, and **Detailed (~500 words)**.
   - Map-reduce chunking for large documents to preserve conclusions and key sections.
   - Automated identification of key topics, financial metrics, and critical dates.
   - Export reports as PDF, DOCX, or TXT.

5. **Semantic Document Search (Module 6)**
   - Neural concept retrieval matching semantics even when exact keywords differ.
   - Highlighted query terms and similarity percentage ratings.

6. **Automated Information Extraction (Module 7)**
   - Regex and heuristic NLP extraction for:
     - Emails and Phone Numbers
     - Financial Amounts & Currencies
     - Significant Dates & Quarters
     - Organizations & Corporate Entities
     - Person Names & Key Stakeholders
     - Headings, Action Items, and Objectives
   - Exportable in CSV, Excel (.xlsx), and JSON formats.

7. **Pairwise Document Comparison (Module 8)**
   - Cosine vector similarity calculation with radial gauges.
   - Shared vocabulary and unique thematic contrasts.
   - Structural gap analysis identifying missing headings between Document A and Document B.

8. **Document History & Audit Trail (Module 10)**
   - Complete historical ledger of indexed documents with content snapshots.
   - Multi-attribute filtering by filename, status, and document format.
   - Activity audit trail logging uploads, queries, extractions, and comparisons.

9. **Settings & RAG Tuning (Module 12)**
   - Dynamic sliders for Chunk Size, Chunk Overlap, and Top-K retrieval.
   - Modular inference routing: **Extractive Built-In (Zero-Cost Offline)**, **Ollama (Local LLM)**, **OpenAI**, and **Gemini**.
   - Storage inspection and database maintenance utilities.

---

## 🏗️ Architecture & RAG Pipeline

```
[Uploaded File (PDF, DOCX, TXT)]
           │
           ▼
[Document Processor] ── (SHA-256 Deduplication & Scanned PDF Check)
           │
           ▼
[Text Chunker] ──────── (Configurable Size & Overlap, Preserves Page Numbers)
           │
           ▼
[Sentence Transformers] (Dense Embeddings: all-MiniLM-L6-v2)
           │
           ▼
[FAISS Vector Store] ── (IndexFlatIP Cosine Similarity & Metadata Mapping)
           ▲
           │ Query Vector
[User Question]
           │
           ▼
[Context Retrieval] ─── (Top-K Matches + Document Scope Filter)
           │
           ▼
[Prompt Shielding] ──── (System Prompt Anti-Injection + Grounding Boundary)
           │
           ▼
[LLM Engine] ────────── (Extractive / Ollama / OpenAI / Gemini)
           │
           ▼
[Grounded Answer with Page-Level Citations & Excerpts]
```

---

## 🛠️ Technology Stack

| Component | Library / Technology |
|---|---|
| **Frontend Framework** | Streamlit |
| **Document Processing** | PyPDF, python-docx |
| **Vector Similarity** | FAISS (faiss-cpu) |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Database** | SQLite3 (WAL Mode & Foreign Key Cascades) |
| **Data & Visualizations** | Pandas, Plotly Express & Graph Objects |
| **Report Generation** | ReportLab (PDF), python-docx (DOCX), openpyxl (XLSX) |
| **Testing** | Pytest (18 automated tests) |

---

## 💻 macOS Installation & Execution Guide

Follow these exact terminal commands to set up and launch AskFile AI on macOS:

### 1. Open Terminal and Navigate to Project
```bash
cd /Users/vishnupradapmrs/.gemini/antigravity/scratch/AskFile-AI
```

### 2. Verify Python 3 Installation
```bash
python3 --version
```

### 3. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Initialize the Database
```bash
python -m database.migrations
```

### 6. (Optional) Configure Environment Variables
Copy `.env.example` to `.env` if you wish to configure an external LLM or custom parameters:
```bash
cp .env.example .env
```

### 7. Run the Automated Test Suite
Verify all 18 automated tests pass:
```bash
pytest -v
```

### 8. Launch the Streamlit Application
```bash
streamlit run app.py
```

The application will open automatically in your browser at:
**`http://localhost:8501`**

---

## 🦙 (Optional) Local LLM Setup with Ollama

AskFile AI includes a **zero-cost, offline extractive synthesizer** by default that requires no third-party APIs. To use local generative LLMs via Ollama:

1. Install Ollama:
   ```bash
   brew install ollama
   ```
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. In a separate terminal, pull a lightweight model:
   ```bash
   ollama run llama3.2
   ```
4. In AskFile AI, navigate to **Settings** (`pages/10_Settings.py`) and select **Ollama** as your LLM Provider.

---

## ☁️ Streamlit Community Cloud Deployment Notes

When deploying to Streamlit Community Cloud:
- **Local Ollama:** Local Ollama daemon instances are not accessible from the public cloud. Switch the LLM Provider to **Extractive** (built-in offline synthesis) or configure `OPENAI_API_KEY` / `GEMINI_API_KEY` in Streamlit Cloud Secrets.
- **Persistent Storage:** Cloud containers have ephemeral local filesystems. For production multi-user cloud persistence, connect SQLite to an external database (e.g., PostgreSQL or Supabase) and mount S3 for uploaded binary files.

---

## 🧪 Testing Verification

The project includes 18 automated tests covering all modules:
- Document extraction (`.pdf`, `.docx`, `.txt`)
- Empty file rejection and invalid extension validation
- Cryptographic SHA-256 deduplication
- Database CRUD, cascading chunk removal, and conversation logging
- Text chunking with metadata preservation
- Dense vector embedding generation and FAISS indexing
- Document-level filtering (anti-cross-contamination)
- RAG grounded question answering with mocked LLM
- Semantic search scoring and term highlighting
- Hierarchical summarization and entity extraction
- Pairwise document comparison
- PDF, DOCX, TXT, CSV, XLSX, and JSON report generation

Execute all tests with:
```bash
pytest -v
```

---

## 📄 License
This project is released under the MIT License.
