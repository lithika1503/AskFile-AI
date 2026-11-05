"""
AskFile AI - Main Application Entrypoint
An Intelligent File Analysis and Question Answering System Using Streamlit & RAG
"""

import streamlit as st
from config import APP_NAME, APP_SUBTITLE, APP_VERSION
from database.migrations import init_db
from database.repository import AnalyticsRepository, ActivityRepository
from utils.ui import (
    apply_custom_theme,
    render_header,
    render_metric_card,
    render_sidebar_branding
)

# Initialize database schema on startup
init_db()

st.set_page_config(
    page_title=f"{APP_NAME} | Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_theme()

# Fetch live real-time stats
stats = AnalyticsRepository.get_overview_stats()

# Global Sidebar Header & Telemetry Chips
render_sidebar_branding(stats)
with st.sidebar:
    st.info("💡 **Navigation:** Use the modules above to upload documents, ask questions, extract structured tables, or generate executive summaries.")

# Hero Header Banner
render_header(
    title=f"Welcome to {APP_NAME}",
    subtitle="High-Performance RAG Platform for Semantic Analysis, Document QA, and Information Extraction"
)

# Top Metrics Row (Responsive 4-column layout)
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Total Documents", str(stats["total_documents"]), "Indexed PDF, DOCX, & TXT")
with col2:
    render_metric_card("Processed Words", f"{stats['total_words']:,}", "Cleaned and tokenized")
with col3:
    render_metric_card("Questions Asked", str(stats["total_questions"]), "Source-grounded RAG answers")
with col4:
    success_rate = (
        round((stats["processed_documents"] / max(1, stats["total_documents"])) * 100)
        if stats["total_documents"] > 0 else 100
    )
    render_metric_card("Health & Reliability", f"{success_rate}%", "Document ingestion rate")

st.markdown("<br>", unsafe_allow_html=True)

# Main Quick Access Hub (Unified Cards with Integrated Action Buttons)
st.markdown("### 🚀 Quick Access Hub")
st.caption("Select a core capability below to start interacting with your documents:")

# Row 1
r1_c1, r1_c2, r1_c3 = st.columns(3)

with r1_c1:
    with st.container(border=True):
        st.markdown("#### 📤 1. Upload Documents")
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.88rem; min-height: 48px;'>"
            "Upload PDF, DOCX, and TXT files. Automatic SHA-256 deduplication, layout preservation, and FAISS indexing."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button("Go to Uploads →", key="btn_upload", use_container_width=True):
            st.switch_page("pages/2_Document_Upload.py")

with r1_c2:
    with st.container(border=True):
        st.markdown("#### 💬 2. AI Chat & RAG")
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.88rem; min-height: 48px;'>"
            "Ask conversational questions grounded strictly in your documents with verified page citations and excerpts."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button("Open AI Chat →", key="btn_chat", use_container_width=True):
            st.switch_page("pages/3_AI_Chat.py")

with r1_c3:
    with st.container(border=True):
        st.markdown("#### 📝 3. Document Summarizer")
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.88rem; min-height: 48px;'>"
            "Generate Executive, Short, Medium, or Detailed summaries with key dates, figures, and exports to PDF/DOCX/TXT."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button("Summarize Docs →", key="btn_summary", use_container_width=True):
            st.switch_page("pages/4_Summarizer.py")

# Row 2
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    with st.container(border=True):
        st.markdown("#### 🔍 4. Smart Search")
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.88rem; min-height: 48px;'>"
            "Semantic vector search matching concepts and context even when exact keywords differ, with highlighted results."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button("Search Passages →", key="btn_search", use_container_width=True):
            st.switch_page("pages/5_Smart_Search.py")

with r2_c2:
    with st.container(border=True):
        st.markdown("#### 📊 5. Info Extraction")
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.88rem; min-height: 48px;'>"
            "Extract emails, phone numbers, financial amounts, key dates, organizations, and action items into CSV/Excel/JSON."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button("Extract Data →", key="btn_extract", use_container_width=True):
            st.switch_page("pages/6_Information_Extraction.py")

with r2_c3:
    with st.container(border=True):
        st.markdown("#### ⚖️ 6. Document Comparison")
        st.markdown(
            "<p style='color: #94A3B8; font-size: 0.88rem; min-height: 48px;'>"
            "Compare two documents side-by-side using vector cosine similarity, common topics, and semantic contrast analysis."
            "</p>",
            unsafe_allow_html=True
        )
        if st.button("Compare Documents →", key="btn_compare", use_container_width=True):
            st.switch_page("pages/7_Document_Comparison.py")

# Recent Activity Feed
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📋 Recent System Activity")
try:
    recent_logs = ActivityRepository.get_recent(5)
except Exception:
    recent_logs = []
if recent_logs:
    for log in recent_logs:
        st.markdown(
            f"""
            <div style="background-color: #0F172A; border: 1px solid rgba(255, 255, 255, 0.08); border-left: 3px solid #3B82F6; padding: 0.65rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.88rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #38BDF8; font-weight: 700; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; background: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 4px; margin-right: 0.5rem;">{log['activity_type']}</span> 
                    <span style="color: #F8FAFC;">{log['activity_description']}</span>
                </div>
                <span style="color: #64748B; font-size: 0.8rem; font-family: monospace;">{log['created_at']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No activity logged yet. Upload your first document to get started!")
