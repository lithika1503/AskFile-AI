"""
Module 10: Document History & Audit Log
Inspect historical records, filter by format/status, review activity trails, and securely purge documents.
"""

import streamlit as st
import pandas as pd
from config import APP_NAME
from database.repository import DocumentRepository, AnalyticsRepository, MessageRepository, ActivityRepository
from services.upload_service import UploadService
from utils.helpers import format_file_size, format_timestamp
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Document History", page_icon="📜", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Document History & System Audit", "Complete historical ledger of ingested assets, vector records, and operational logs")

upload_service = UploadService()
docs = DocumentRepository.get_all()

# Filters Row
f_col1, f_col2, f_col3 = st.columns(3)
with f_col1:
    search_term = st.text_input("🔍 Search documents by name:", placeholder="Filter by keyword...")
with f_col2:
    status_filter = st.selectbox("Filter by Status:", options=["All", "Completed", "Failed", "Processing"])
with f_col3:
    type_filter = st.selectbox("Filter by Format:", options=["All", "PDF", "DOCX", "TXT"])

# Apply Filters
filtered_docs = docs
if search_term.strip():
    filtered_docs = [d for d in filtered_docs if search_term.lower() in d.filename.lower()]
if status_filter != "All":
    filtered_docs = [d for d in filtered_docs if d.processing_status.lower() == status_filter.lower()]
if type_filter != "All":
    filtered_docs = [d for d in filtered_docs if d.file_type.lower() == type_filter.lower()]

st.markdown(f"**Showing {len(filtered_docs)} of {len(docs)} document(s)**")

if not filtered_docs:
    render_empty_state("No Matching Documents", "No records found matching the active search and filter criteria.")
else:
    for doc in filtered_docs:
        status_color = "#10B981" if doc.processing_status == "completed" else "#EF4444"
        with st.expander(f"📄 {doc.filename} — {format_timestamp(doc.upload_date)} ({doc.file_type.upper()})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Document ID:** `{doc.id}`")
                st.markdown(f"**File Size:** `{format_file_size(doc.file_size)}`")
                st.markdown(f"**Status:** <span style='color:{status_color}; font-weight:600;'>{doc.processing_status.upper()}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**Total Pages:** `{doc.page_count}`")
                st.markdown(f"**Total Words:** `{doc.word_count:,}`")
                st.markdown(f"**Uploaded On:** {format_timestamp(doc.upload_date)}")
            with c3:
                st.markdown(f"**SHA-256 Hash:**")
                st.caption(f"`{doc.file_hash}`")
                if st.button("🗑️ Delete from System", key=f"hist_del_{doc.id}", type="secondary"):
                    success, msg = upload_service.delete_document(doc.id)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("---")
            st.markdown("##### 📄 Content Snapshot")
            snippet = doc.extracted_text[:1000] if doc.extracted_text else "[No extracted text]"
            st.text_area("Extracted Text Preview", snippet, height=120, disabled=True, key=f"snip_{doc.id}")

st.markdown("<br>", unsafe_allow_html=True)

# System Activity Ledger
st.markdown("### 📋 Activity Audit Trail")
try:
    logs = ActivityRepository.get_recent(25)
except Exception:
    logs = []
if logs:
    df_logs = pd.DataFrame([
        {
            "Action": l["activity_type"],
            "Description": l["activity_description"],
            "Document": l.get("filename") or "System / Multi-Doc",
            "Timestamp": l["created_at"]
        }
        for l in logs
    ])
    st.dataframe(df_logs, use_container_width=True)
else:
    st.info("No audit logs recorded.")
