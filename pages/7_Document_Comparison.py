"""
Module 8: Document Comparison Engine
Pairwise semantic vector comparison, thematic overlap, missing section detection,
and AI-assisted comparative narrative.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import APP_NAME
from database.repository import DocumentRepository, ActivityRepository, AnalyticsRepository
from core.comparison_engine import DocumentComparisonEngine
from utils.constants import ACTIVITY_COMPARE
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Document Comparison", page_icon="⚖️", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Document Comparison & Contrast", "Evaluate semantic alignment, common vocabulary, and thematic divergences between documents")

comparison_engine = DocumentComparisonEngine()

docs = [d for d in DocumentRepository.get_all() if d.processing_status == "completed"]

if len(docs) < 2:
    render_empty_state(
        "Insufficient Documents for Comparison",
        "At least two completed documents are required to perform comparative analysis. "
        "Please upload additional documents in Document Upload."
    )
else:
    doc_options = {d.id: f"{d.filename} ({d.file_type.upper()})" for d in docs}

    c_col1, c_col2 = st.columns(2)
    with c_col1:
        doc_a_id = st.selectbox(
            "Document A (Baseline):",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
            index=0
        )
    with c_col2:
        # Default Document B to the second document
        doc_b_id = st.selectbox(
            "Document B (Target):",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options[x],
            index=1 if len(doc_options) > 1 else 0
        )

    if doc_a_id == doc_b_id:
        st.warning("Please choose two different documents to compare.")
    else:
        doc_a = DocumentRepository.get_by_id(doc_a_id)
        doc_b = DocumentRepository.get_by_id(doc_b_id)

        if st.button("⚖️ Compare Documents", type="primary"):
            with st.spinner(f"Computing embeddings and analyzing '{doc_a.filename}' vs '{doc_b.filename}'..."):
                res = comparison_engine.compare(
                    doc_a_name=doc_a.filename,
                    doc_a_text=doc_a.extracted_text,
                    doc_b_name=doc_b.filename,
                    doc_b_text=doc_b.extracted_text
                )
                st.session_state["comparison_result"] = res
                ActivityRepository.log(
                    ACTIVITY_COMPARE,
                    f"Compared '{doc_a.filename}' vs '{doc_b.filename}' ({res['similarity_percentage']}% sim)",
                    doc_a.id
                )

        if "comparison_result" in st.session_state:
            res = st.session_state["comparison_result"]

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"### 📊 Comparative Analysis: {res['doc_a_name']} vs {res['doc_b_name']}")

            # Similarity Gauge Card
            g_col1, g_col2 = st.columns([1, 2])
            with g_col1:
                # Radial Gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=res["similarity_percentage"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Semantic Similarity", 'font': {'color': '#F8FAFC', 'size': 16}},
                    number={'suffix': "%", 'font': {'color': '#38BDF8', 'size': 32}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': "#94A3B8"},
                        'bar': {'color': "#3B82F6"},
                        'steps': [
                            {'range': [0, 40], 'color': "#1E293B"},
                            {'range': [40, 75], 'color': "#0F172A"},
                            {'range': [75, 100], 'color': "#1E3A8A"}
                        ]
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=240,
                    margin=dict(t=30, b=10, l=20, r=20)
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            with g_col2:
                st.markdown(
                    f"""
                    <div class="askfile-card" style="height: 210px; overflow-y: auto;">
                        <b style="color: #38BDF8;">Methodology &amp; Alignment</b><br>
                        <span style="font-size: 0.85rem; color: #94A3B8;">Method: {res['similarity_metric']}</span><br>
                        <span style="font-size: 0.85rem; color: #94A3B8;">Lexical Jaccard Overlap: {res['jaccard_overlap_percentage']}%</span><br><br>
                        <div style="font-size: 0.88rem; color: #E2E8F0;">
                            <b>Summary Comparison:</b><br>
                            {res['comparison_summary']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(f"ℹ️ {res['disclaimer']}")

            # Thematic breakdown
            st.markdown("<br>", unsafe_allow_html=True)
            top_col1, top_col2, top_col3 = st.columns(3)

            with top_col1:
                st.markdown(f"##### 🤝 Shared Topics ({len(res['common_topics'])})")
                if res["common_topics"]:
                    st.write(", ".join([f"`{t}`" for t in res["common_topics"]]))
                else:
                    st.caption("No significant vocabulary overlap.")

            with top_col2:
                st.markdown(f"##### 🟦 Unique to {doc_a.filename[:15]}...")
                if res["unique_to_doc_a"]:
                    st.write(", ".join([f"`{t}`" for t in res["unique_to_doc_a"]]))
                else:
                    st.caption("No unique topics found.")

            with top_col3:
                st.markdown(f"##### 🟩 Unique to {doc_b.filename[:15]}...")
                if res["unique_to_doc_b"]:
                    st.write(", ".join([f"`{t}`" for t in res["unique_to_doc_b"]]))
                else:
                    st.caption("No unique topics found.")

            # Section & Structural Divergence
            st.markdown("---")
            st.markdown("##### 📑 Structural Divergence")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown(f"**Sections in Doc A missing from Doc B:**")
                if res["missing_in_doc_b"]:
                    for h in res["missing_in_doc_b"]:
                        st.markdown(f"- ⚠️ `{h}`")
                else:
                    st.success("No major headings missing in Doc B.")
            with s_col2:
                st.markdown(f"**Sections in Doc B missing from Doc A:**")
                if res["missing_in_doc_a"]:
                    for h in res["missing_in_doc_a"]:
                        st.markdown(f"- ⚠️ `{h}`")
                else:
                    st.success("No major headings missing in Doc A.")
