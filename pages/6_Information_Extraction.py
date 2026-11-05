"""
Module 7: Automatic Information Extraction
Isolates structured entities, contacts, financial figures, headings, objectives,
and conclusions with tabular CSV, Excel, and JSON downloads.
"""

import streamlit as st
import pandas as pd
from config import APP_NAME
from database.repository import DocumentRepository, ActivityRepository, AnalyticsRepository
from core.information_extractor import InformationExtractor
from services.export_service import ExportService
from utils.constants import ACTIVITY_EXTRACT
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Information Extraction", page_icon="📊", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Automated Information Extraction", "Heuristic entity identification, contact intelligence, and structured data exports")

docs = [d for d in DocumentRepository.get_all() if d.processing_status == "completed"]

if not docs:
    render_empty_state(
        "No Documents Found",
        "Upload a document in Document Upload before running entity extraction."
    )
else:
    doc_options = {d.id: f"{d.filename} ({d.word_count:,} words)" for d in docs}
    selected_id = st.selectbox(
        "Select Document to Analyze:",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x]
    )

    doc = DocumentRepository.get_by_id(selected_id)

    if st.button("⚡ Extract Entities & Key Metadata", type="primary"):
        with st.spinner("Extracting entities, headings, financials, and action items..."):
            extracted = InformationExtractor.extract_all(doc.extracted_text)
            st.session_state["extracted_data"] = extracted
            st.session_state["extracted_doc_name"] = doc.filename
            ActivityRepository.log(
                ACTIVITY_EXTRACT,
                f"Extracted {extracted.get('total_entities_found', 0)} entities from '{doc.filename}'",
                doc.id
            )

    if "extracted_data" in st.session_state and st.session_state.get("extracted_doc_name") == doc.filename:
        data = st.session_state["extracted_data"]

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### 📋 Extraction Results: {doc.filename}")
        st.caption(f"Total structured items identified: {data.get('total_entities_found', 0)}")

        # Entity Tabs
        tab_contacts, tab_financials, tab_orgs, tab_actions, tab_headings = st.tabs([
            "📞 Contacts & Emails",
            "💰 Financials & Dates",
            "🏢 Organizations & People",
            "🎯 Objectives & Action Items",
            "📑 Headings & Key Terms"
        ])

        with tab_contacts:
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                st.markdown("##### ✉️ Email Addresses")
                if data["emails"]:
                    st.dataframe(pd.DataFrame({"Email": data["emails"]}), use_container_width=True)
                else:
                    st.info("No email addresses detected.")
            with c_col2:
                st.markdown("##### 📱 Phone Numbers")
                if data["phones"]:
                    st.dataframe(pd.DataFrame({"Phone Number": data["phones"]}), use_container_width=True)
                else:
                    st.info("No phone numbers detected.")

        with tab_financials:
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown("##### 💵 Financial Amounts & Currencies")
                if data["financials"]:
                    st.dataframe(pd.DataFrame({"Amount": data["financials"]}), use_container_width=True)
                else:
                    st.info("No monetary amounts detected.")
            with f_col2:
                st.markdown("##### 📅 Significant Dates")
                if data["dates"]:
                    st.dataframe(pd.DataFrame({"Date / Quarter": data["dates"]}), use_container_width=True)
                else:
                    st.info("No dates detected.")

        with tab_orgs:
            o_col1, o_col2 = st.columns(2)
            with o_col1:
                st.markdown("##### 🏢 Organizations & Companies")
                if data["organizations"]:
                    st.dataframe(pd.DataFrame({"Organization": data["organizations"]}), use_container_width=True)
                else:
                    st.info("No explicit corporate entities detected.")
            with o_col2:
                st.markdown("##### 👤 Person Names / Key Stakeholders")
                if data["person_names"]:
                    st.dataframe(pd.DataFrame({"Name": data["person_names"]}), use_container_width=True)
                else:
                    st.info("No formal person names with honorifics detected.")

        with tab_actions:
            a_col1, a_col2 = st.columns(2)
            with a_col1:
                st.markdown("##### 🎯 Document Objectives")
                if data["objectives"]:
                    for obj in data["objectives"]:
                        st.markdown(f"- {obj}")
                else:
                    st.info("No explicit objectives statements isolated.")
            with a_col2:
                st.markdown("##### ✅ Action Items & Requirements")
                if data["action_items"]:
                    for act in data["action_items"]:
                        st.markdown(f"- {act}")
                else:
                    st.info("No imperative action items isolated.")

        with tab_headings:
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                st.markdown("##### 📑 Document Structure & Headings")
                if data["headings"]:
                    st.dataframe(pd.DataFrame({"Heading": data["headings"]}), use_container_width=True)
                else:
                    st.info("No structured headings detected.")
            with h_col2:
                st.markdown("##### 🔑 Prominent Key Terms")
                if data["key_terms"]:
                    st.write(", ".join([f"`{t}`" for t in data["key_terms"]]))
                else:
                    st.info("No significant keywords isolated.")

        # Export Row
        st.markdown("---")
        st.markdown("##### 📥 Export Extracted Entities")
        exp1, exp2, exp3 = st.columns(3)

        with exp1:
            csv_data = ExportService.export_extraction_csv(data)
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name=f"{doc.filename}_extracted.csv",
                mime="text/csv",
                use_container_width=True
            )

        with exp2:
            xlsx_data = ExportService.export_extraction_xlsx(data)
            st.download_button(
                "📥 Download Excel (.xlsx)",
                data=xlsx_data,
                file_name=f"{doc.filename}_extracted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with exp3:
            json_data = ExportService.export_extraction_json(data)
            st.download_button(
                "📥 Download JSON",
                data=json_data,
                file_name=f"{doc.filename}_extracted.json",
                mime="application/json",
                use_container_width=True
            )
