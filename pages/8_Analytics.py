"""
Module 9: In-Depth Document Analytics
Aggregated telemetry, distribution models, and repository trends powered by SQLite and Plotly.
"""

import streamlit as st
import pandas as pd
from config import APP_NAME
from database.repository import AnalyticsRepository, DocumentRepository
from services.analytics_service import AnalyticsService
from utils.helpers import format_file_size, format_timestamp
from utils.ui import apply_custom_theme, render_header, render_metric_card, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | Analytics", page_icon="📈", layout="wide")
apply_custom_theme()

metrics = AnalyticsService.get_dashboard_metrics()
render_sidebar_branding(metrics)

render_header("Document Analytics & Intelligence", "Corpus volume, processing health, and semantic search metrics")

# Top KPI Metric Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    render_metric_card("Total Documents", str(metrics["total_documents"]), f"Active: {metrics['processed_documents']}")
with kpi2:
    render_metric_card("Total Words Processed", metrics["formatted_total_words"], f"Mean: {int(metrics['avg_word_count']):,} words")
with kpi3:
    render_metric_card("Average File Size", metrics["formatted_avg_size"], "Disk storage footprint")
with kpi4:
    render_metric_card("Conversational Queries", str(metrics["total_questions"]), "Recorded in messages")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row 1: Donut & Status Bars
c1, c2 = st.columns(2)
with c1:
    st.markdown("#### 📁 File Format Distribution")
    fig1 = AnalyticsService.create_file_type_chart()
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("#### ⚡ Processing Reliability")
    fig2 = AnalyticsService.create_processing_status_chart()
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations Row 2: Ingestion Timeline & Activity Mix
c3, c4 = st.columns(2)
with c3:
    st.markdown("#### 📅 Cumulative Uploads Timeline")
    fig3 = AnalyticsService.create_uploads_timeline_chart()
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown("#### 📊 System Action Breakdown")
    fig4 = AnalyticsService.create_activity_breakdown_chart()
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Top Documents by Word Count
st.markdown("#### 📚 Document Corpus Summary Table")
docs = DocumentRepository.get_all()
if docs:
    table_data = [
        {
            "Filename": d.filename,
            "Type": d.file_type.upper(),
            "Size": format_file_size(d.file_size),
            "Word Count": f"{d.word_count:,}",
            "Pages": d.page_count,
            "Status": d.processing_status.capitalize(),
            "Uploaded": format_timestamp(d.upload_date)
        }
        for d in docs
    ]
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)
else:
    st.info("No documents currently stored in repository.")
