"""
Module 2: Document Upload & Repository Management
Supports multi-file upload, SHA-256 deduplication, text preview, reprocessing, and deletion.
"""

import streamlit as st
import pandas as pd
from config import APP_NAME, MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS
from database.repository import DocumentRepository, AnalyticsRepository
from services.upload_service import UploadService
from utils.helpers import format_file_size, format_timestamp
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Document Upload", page_icon="📤", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Document Upload & Ingestion", "Upload, validate, and index PDF, DOCX, and TXT files into FAISS vector storage")

upload_service = UploadService()

# -------------------------------------------------------------
# Upload Section
# -------------------------------------------------------------
st.markdown("### 📤 Upload New Documents")
uploaded_files = st.file_uploader(
    f"Drag and drop documents here (Max {MAX_FILE_SIZE_MB}MB each. Supported: PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button(f"Process {len(uploaded_files)} Document(s)", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, file in enumerate(uploaded_files):
            status_text.text(f"Processing ({idx+1}/{len(uploaded_files)}): {file.name}...")
            file_bytes = file.read()
            file_size = len(file_bytes)

            success, msg, doc = upload_service.process_upload(
                filename=file.name,
                file_bytes=file_bytes,
                file_size=file_size
            )

            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")

            progress_bar.progress((idx + 1) / len(uploaded_files))

        status_text.text("Ingestion completed!")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Uploaded Documents Repository
# -------------------------------------------------------------
st.markdown("### 📚 Managed Document Library")
docs = DocumentRepository.get_all()

if not docs:
    render_empty_state(
        "No Documents Found",
        "Upload your first PDF, DOCX, or TXT file above to start analyzing documents."
    )
else:
    # Action Table with expanders
    for doc in docs:
        status_color = "#10B981" if doc.processing_status == "completed" else "#EF4444"
        with st.expander(f"📄 **{doc.filename}** ({doc.file_type.upper()}) — {format_file_size(doc.file_size)} — Status: {doc.processing_status.upper()}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"**Document ID:** `{doc.id[:8]}...`")
                st.markdown(f"**Uploaded:** {format_timestamp(doc.upload_date)}")
            with col2:
                st.markdown(f"**Pages / Sections:** `{doc.page_count}`")
                st.markdown(f"**Word Count:** `{doc.word_count:,}`")
            with col3:
                st.markdown(f"**File Size:** `{format_file_size(doc.file_size)}`")
                st.markdown(f"**Status:** <span style='color:{status_color}; font-weight:600;'>{doc.processing_status.capitalize()}</span>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"**SHA-256 Hash:**")
                st.caption(f"`{doc.file_hash[:16]}...`")

            # Document Actions: Reprocess & Delete
            act_col1, act_col2 = st.columns([1, 1])
            with act_col1:
                if st.button("🔄 Reprocess Document", key=f"reproc_{doc.id}"):
                    success, r_msg = upload_service.reprocess_document(doc.id)
                    if success:
                        st.success(r_msg)
                        st.rerun()
                    else:
                        st.error(r_msg)

            with act_col2:
                if st.button("🗑️ Delete Document", key=f"del_{doc.id}", type="secondary"):
                    success, d_msg = upload_service.delete_document(doc.id)
                    if success:
                        st.success(d_msg)
                        st.rerun()
                    else:
                        st.error(d_msg)

            # Extracted Text Preview
            st.markdown("---")
            st.markdown("##### 🔍 Extracted Text Preview")
            if doc.extracted_text:
                preview_text = doc.extracted_text[:1500] + ("\n\n... [remaining text truncated for preview] ..." if len(doc.extracted_text) > 1500 else "")
                st.text_area("Extracted Content", preview_text, height=180, disabled=True, key=f"txt_{doc.id}")
            else:
                st.warning("No text extracted for this document. It may have failed or require OCR.")
