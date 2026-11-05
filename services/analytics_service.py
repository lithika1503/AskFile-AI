"""Analytics service generating summary metrics and Plotly charts from SQLite."""

from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.repository import AnalyticsRepository
from utils.helpers import format_file_size

class AnalyticsService:
    """Aggregates database metrics and builds responsive Plotly visualization figures."""

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Fetches raw numeric stats for dashboard cards."""
        stats = AnalyticsRepository.get_overview_stats()
        stats["formatted_avg_size"] = format_file_size(int(stats["avg_file_size"]))
        stats["formatted_total_words"] = f"{int(stats['total_words']):,}"
        return stats

    @staticmethod
    def create_file_type_chart() -> go.Figure:
        """Donut chart for document type distribution."""
        dist = AnalyticsRepository.get_document_type_distribution()
        if not dist:
            fig = go.Figure()
            fig.update_layout(
                title="No documents uploaded yet",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8")
            )
            return fig

        df = pd.DataFrame(dist)
        df["file_type"] = df["file_type"].str.upper()

        fig = px.pie(
            df,
            names="file_type",
            values="count",
            hole=0.55,
            color_discrete_sequence=["#3B82F6", "#10B981", "#8B5CF6", "#F59E0B"]
        )
        fig.update_layout(
            margin=dict(t=30, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig

    @staticmethod
    def create_processing_status_chart() -> go.Figure:
        """Bar chart of document processing status."""
        dist = AnalyticsRepository.get_processing_status_distribution()
        if not dist:
            fig = go.Figure()
            fig.update_layout(
                title="No processing data available",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8")
            )
            return fig

        df = pd.DataFrame(dist)
        df["processing_status"] = df["processing_status"].str.capitalize()
        color_map = {"Completed": "#10B981", "Failed": "#EF4444", "Processing": "#F59E0B"}

        fig = px.bar(
            df,
            x="processing_status",
            y="count",
            color="processing_status",
            color_discrete_map=color_map,
            text="count"
        )
        fig.update_layout(
            margin=dict(t=30, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            xaxis_title="Processing Status",
            yaxis_title="Count",
            showlegend=False
        )
        fig.update_traces(textposition="outside")
        return fig

    @staticmethod
    def create_uploads_timeline_chart() -> go.Figure:
        """Time-series line chart for uploads over time."""
        timeline = AnalyticsRepository.get_uploads_over_time()
        if not timeline:
            fig = go.Figure()
            fig.update_layout(
                title="No upload timeline data available",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8")
            )
            return fig

        df = pd.DataFrame(timeline)
        fig = px.area(
            df,
            x="upload_day",
            y="count",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#3B82F6"]
        )
        fig.update_layout(
            margin=dict(t=30, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            xaxis=dict(showgrid=True, gridcolor="#334155"),
            yaxis=dict(showgrid=True, gridcolor="#334155"),
            xaxis_title="Date",
            yaxis_title="Uploads"
        )
        return fig

    @staticmethod
    def create_activity_breakdown_chart() -> go.Figure:
        """Horizontal bar chart for user activity types."""
        breakdown = AnalyticsRepository.get_activity_breakdown()
        if not breakdown:
            fig = go.Figure()
            fig.update_layout(
                title="No activity recorded",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8")
            )
            return fig

        df = pd.DataFrame(breakdown)
        fig = px.bar(
            df,
            x="count",
            y="activity_type",
            orientation="h",
            color="activity_type",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig.update_layout(
            margin=dict(t=30, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC"),
            yaxis_title="Action",
            xaxis_title="Occurrences",
            showlegend=False
        )
        return fig
