"""
Module 4: AI Document Summarizer
Multi-tier document condensation (Short, Medium, Detailed, Executive) with key findings,
dates, figures, and exports to PDF, DOCX, and TXT.
"""

import streamlit as st
from config import APP_NAME
from database.repository import DocumentRepository, ActivityRepository, AnalyticsRepository
from core.summarizer import DocumentSummarizer
from services.export_service import ExportService
from utils.constants import ACTIVITY_SUMMARIZE
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Summarizer", page_icon="📝", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("AI Document Summarizer", "Hierarchical synthesis, executive briefings, and significant numerical highlights")

summarizer = DocumentSummarizer()

# Document Selection
docs = [d for d in DocumentRepository.get_all() if d.processing_status == "completed"]

if not docs:
    render_empty_state(
        "No Documents Available",
        "Upload a document in Document Upload before generating summaries."
    )
else:
    doc_map = {d.id: f"{d.filename} ({d.word_count:,} words)" for d in docs}
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_id = st.selectbox(
            "Select Document to Summarize:",
            options=list(doc_map.keys()),
            format_func=lambda x: doc_map[x]
        )
    with col2:
        mode = st.selectbox(
            "Summary Scope:",
            options=["Executive", "Short (~100 words)", "Medium (~300 words)", "Detailed (~500 words)"],
            index=0
        )

    clean_mode = mode.split()[0].lower()

    target_doc = DocumentRepository.get_by_id(selected_id)

    if st.button("✨ Generate Summary", type="primary"):
        with st.spinner(f"Analyzing '{target_doc.filename}' with hierarchical summarizer..."):
            summary_result = summarizer.summarize(
                document_text=target_doc.extracted_text,
                filename=target_doc.filename,
                mode=clean_mode
            )
            st.session_state["active_summary"] = summary_result
            st.session_state["active_summary_doc"] = target_doc.filename
            ActivityRepository.log(
                ACTIVITY_SUMMARIZE,
                f"Generated {clean_mode} summary for '{target_doc.filename}'",
                target_doc.id
            )

    # Render Active Summary
    if "active_summary" in st.session_state and st.session_state.get("active_summary_doc") == target_doc.filename:
        res = st.session_state["active_summary"]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### 📋 Summary Report: {target_doc.filename}")
        
        # Summary body card
        st.markdown(
            f"""
            <div class="askfile-card">
                {res['summary']}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Highlights row
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            st.markdown("##### 🔑 Key Topics Identified")
            if res.get("key_topics"):
                st.write(", ".join([f"`{t}`" for t in res["key_topics"]]))
            else:
                st.caption("No specific topics isolated.")

        with h_col2:
            st.markdown("##### 📅 Significant Dates & Numbers")
            if res.get("dates_and_figures"):
                for df in res["dates_and_figures"]:
                    st.markdown(f"- {df}")
            else:
                st.caption("No financial figures or explicit dates found.")

        # Download Export Options
        st.markdown("---")
        st.markdown("##### 📥 Export Summary")
        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            pdf_bytes = ExportService.export_summary_pdf(target_doc.filename, res)
            st.download_button(
                "📥 Download PDF Report",
                data=pdf_bytes,
                file_name=f"{target_doc.filename}_summary.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with exp_col2:
            docx_bytes = ExportService.export_summary_docx(target_doc.filename, res)
            st.download_button(
                "📥 Download Word (.docx)",
                data=docx_bytes,
                file_name=f"{target_doc.filename}_summary.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        with exp_col3:
            txt_bytes = ExportService.export_summary_txt(target_doc.filename, res)
            st.download_button(
                "📥 Download Text (.txt)",
                data=txt_bytes,
                file_name=f"{target_doc.filename}_summary.txt",
                mime="text/plain",
                use_container_width=True
            )
