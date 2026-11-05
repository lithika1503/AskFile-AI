"""
Module 1: Dashboard & System Overview
Visualizes live metrics, file breakdowns, and processing health from SQLite.
"""

import streamlit as st
from config import APP_NAME
from database.repository import AnalyticsRepository, DocumentRepository, ActivityRepository
from services.analytics_service import AnalyticsService
from utils.ui import apply_custom_theme, render_header, render_metric_card, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Dashboard", page_icon="📊", layout="wide")
apply_custom_theme()

# Fetch real-time statistics
metrics = AnalyticsService.get_dashboard_metrics()
render_sidebar_branding(metrics)

render_header("Executive Dashboard", "Live Analytics, Ingestion Statistics & System Health")

# Top Metric Cards
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    render_metric_card("Total Documents", str(metrics["total_documents"]), f"Processed: {metrics['processed_documents']}")
with m_col2:
    render_metric_card("Total Words Extracted", metrics["formatted_total_words"], f"Avg: {int(metrics['avg_word_count']):,} words/doc")
with m_col3:
    render_metric_card("Questions Answered", str(metrics["total_questions"]), "RAG conversational queries")
with m_col4:
    render_metric_card("Average File Size", metrics["formatted_avg_size"], "Calculated across repository")

st.markdown("<br>", unsafe_allow_html=True)

# Charts Row
ch_col1, ch_col2 = st.columns(2)
with ch_col1:
    st.markdown("#### 📁 Document Format Distribution")
    fig_types = AnalyticsService.create_file_type_chart()
    st.plotly_chart(fig_types, use_container_width=True)

with ch_col2:
    st.markdown("#### ⚙️ Document Processing Status")
    fig_status = AnalyticsService.create_processing_status_chart()
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Timeline and Activity
t_col1, t_col2 = st.columns([3, 2])

with t_col1:
    st.markdown("#### 📈 Uploads Timeline")
    fig_timeline = AnalyticsService.create_uploads_timeline_chart()
    st.plotly_chart(fig_timeline, use_container_width=True)

with t_col2:
    st.markdown("#### 🕒 Recent Activity Log")
    try:
        recent_activities = ActivityRepository.get_recent(8)
    except Exception:
        recent_activities = []

    if recent_activities:
        for act in recent_activities:
            st.markdown(
                f"""
                <div style="background-color: #1E293B; border-left: 3px solid #3B82F6; padding: 0.5rem 0.75rem; border-radius: 4px; margin-bottom: 0.4rem; font-size: 0.82rem;">
                    <b>{act['activity_type']}</b>: {act['activity_description'][:80]}
                    <div style="color: #64748B; font-size: 0.75rem;">{act['created_at']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No activity logged yet.")
