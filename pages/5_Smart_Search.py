"""
Module 6: Semantic Document Search
Natural language neural search across FAISS chunks with term highlighting and relevance scores.
"""

import streamlit as st
from config import APP_NAME
from database.repository import DocumentRepository, ActivityRepository, AnalyticsRepository
from core.search_engine import SearchEngine
from utils.constants import ACTIVITY_SEARCH
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Smart Search", page_icon="🔍", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Semantic Document Search", "Neural concept search retrieving semantically matched passages even without exact keyword matches")

search_engine = SearchEngine()

docs = [d for d in DocumentRepository.get_all() if d.processing_status == "completed"]

if not docs:
    render_empty_state(
        "No Documents to Search",
        "Please upload documents in Document Upload before running semantic searches."
    )
else:
    doc_options = {d.id: f"{d.filename} ({d.file_type.upper()})" for d in docs}

    s_col1, s_col2 = st.columns([3, 1])
    with s_col1:
        query = st.text_input("Enter natural language search query:", placeholder="e.g., What are the core deliverables and deadlines?")
    with s_col2:
        top_k = st.slider("Max Results:", min_value=1, max_value=10, value=5)

    filter_docs = st.multiselect(
        "Filter search to specific documents (Optional):",
        options=list(doc_options.keys()),
        format_func=lambda x: doc_options[x],
        default=[]
    )

    if st.button("🔍 Search Knowledge Base", type="primary"):
        if not query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner("Embedding query and scanning FAISS vector index..."):
                target_ids = filter_docs if filter_docs else None
                results = search_engine.search(query=query, document_ids=target_ids, top_k=top_k)

                ActivityRepository.log(
                    ACTIVITY_SEARCH,
                    f"Searched for '{query[:40]}' ({len(results)} matches)"
                )

                if not results:
                    st.info("No matching passages found with sufficient relevance. Try rephrasing your search.")
                else:
                    st.markdown(f"#### Found {len(results)} Relevant Passages")
                    for idx, r in enumerate(results, start=1):
                        relevance = r["relevance_percentage"]
                        badge_color = "#10B981" if relevance >= 60 else "#3B82F6" if relevance >= 40 else "#F59E0B"

                        st.markdown(
                            f"""
                            <div class="askfile-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <div>
                                        <b style="color: #38BDF8;">Match #{idx}</b> — 📄 <b>{r['filename']}</b> (Page {r['page_number']})
                                    </div>
                                    <span style="background-color: {badge_color}; color: #FFFFFF; font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 9999px;">
                                        {relevance}% Relevance
                                    </span>
                                </div>
                                <div style="font-size: 0.95rem; line-height: 1.6; color: #E2E8F0; background-color: #0F172A; padding: 1rem; border-radius: 6px; border-left: 3px solid #3B82F6;">
                                    {r['highlighted_html']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
