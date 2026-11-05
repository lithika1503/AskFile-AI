"""
UI Design System and CSS Injector for AskFile AI.
Provides an enterprise Dark Navy glassmorphic theme, responsive layouts,
and consistent component styling across all pages.
"""

import streamlit as st
from config import APP_NAME, APP_SUBTITLE, APP_VERSION

CUSTOM_CSS = """
<style>
/* =====================================================================
   1. Typography & Global Resets
   ===================================================================== */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

code, kbd, samp, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* =====================================================================
   2. Canvas, App Layout & Zero-White Header Fix
   ===================================================================== */
.stApp {
    background-color: #070B14 !important;
    color: #F8FAFC !important;
}

/* Fix Streamlit's white top bar completely */
header[data-testid="stHeader"] {
    background: rgba(7, 11, 20, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    z-index: 99 !important;
}

header[data-testid="stHeader"] svg {
    fill: #94A3B8 !important;
}

/* Main Content Container Padding */
.main .block-container {
    max-width: 1280px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* =====================================================================
   3. Sidebar Navigation & Branding
   ===================================================================== */
section[data-testid="stSidebar"] {
    background: #0B1120 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3) !important;
}

/* Sidebar Nav Items */
[data-testid="stSidebarNav"] {
    padding-top: 0.5rem;
    padding-bottom: 1rem;
}

[data-testid="stSidebarNav"] ul {
    gap: 0.25rem !important;
}

[data-testid="stSidebarNav"] ul li a {
    color: #94A3B8 !important;
    background-color: transparent !important;
    border-radius: 8px !important;
    padding: 0.55rem 0.85rem !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-decoration: none !important;
    border: 1px solid transparent !important;
}

[data-testid="stSidebarNav"] ul li a:hover {
    color: #38BDF8 !important;
    background: rgba(56, 189, 248, 0.08) !important;
    border-color: rgba(56, 189, 248, 0.2) !important;
    transform: translateX(3px);
}

[data-testid="stSidebarNav"] ul li a[aria-current="page"] {
    color: #FFFFFF !important;
    background: linear-gradient(90deg, rgba(37, 99, 235, 0.28) 0%, rgba(30, 58, 138, 0.15) 100%) !important;
    border-left: 3px solid #3B82F6 !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
}

[data-testid="stSidebarNav"] ul li a span {
    color: inherit !important;
}

/* Sidebar Custom Info Card */
.sidebar-brand-card {
    background: linear-gradient(180deg, #131E35 0%, #0D1527 100%);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.sidebar-stat-chip {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 0.45rem 0.75rem;
    margin-top: 0.4rem;
    font-size: 0.82rem;
}

.sidebar-stat-val {
    color: #38BDF8;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

/* =====================================================================
   4. Hero Header & Top Banner
   ===================================================================== */
.askfile-hero {
    background: radial-gradient(120% 120% at 50% 0%, rgba(37, 99, 235, 0.22) 0%, rgba(13, 21, 39, 0.7) 60%, rgba(7, 11, 20, 0.95) 100%);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 16px;
    padding: 2.25rem 2.5rem;
    margin-bottom: 1.75rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.askfile-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: #93C5FD;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    margin-bottom: 0.75rem;
}

.askfile-hero h1 {
    font-size: 2.35rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    letter-spacing: -0.03em !important;
    background: linear-gradient(135deg, #FFFFFF 30%, #93C5FD 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.askfile-hero p {
    color: #94A3B8 !important;
    font-size: 1.02rem !important;
    margin-top: 0.65rem !important;
    margin-bottom: 1rem !important;
    max-width: 800px;
    line-height: 1.55;
}

.askfile-hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 0.5rem;
}

.askfile-hero-tag {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 0.25rem 0.65rem;
    font-size: 0.78rem;
    color: #CBD5E1;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}

/* =====================================================================
   5. High-Impact Metric Cards
   ===================================================================== */
.askfile-metric-card {
    background: linear-gradient(180deg, rgba(23, 34, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.4rem;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    position: relative;
    overflow: hidden;
}

.askfile-metric-card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 12px 28px -8px rgba(37, 99, 235, 0.25);
}

.askfile-metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3B82F6, #60A5FA);
    opacity: 0.7;
}

.metric-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
    margin-bottom: 0.35rem;
}

.metric-value {
    font-size: 2.15rem;
    font-weight: 800;
    color: #38BDF8;
    line-height: 1.1;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.03em;
}

.metric-subtext {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.4rem;
}

/* =====================================================================
   6. Unified Quick-Access SaaS Cards
   ===================================================================== */
div[data-testid="stVerticalBlock"] > div.hub-card-box {
    background: #0F172A;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.5rem;
    transition: all 0.2s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.hub-card-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.hub-card-desc {
    color: #94A3B8;
    font-size: 0.88rem;
    line-height: 1.5;
    margin-bottom: 1.25rem;
    min-height: 48px;
}

/* =====================================================================
   7. Form Controls, Inputs, and Streamlit Elements
   ===================================================================== */
/* Buttons */
.stButton > button {
    background: linear-gradient(180deg, #2563EB 0%, #1D4ED8 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.25rem !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button:hover {
    background: linear-gradient(180deg, #3B82F6 0%, #2563EB 100%) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Secondary Button */
.stButton > button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.7) !important;
    color: #CBD5E1 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: none !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(51, 65, 85, 0.8) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Inputs & Text Areas */
input, textarea, .stSelectbox [data-baseweb="select"] {
    background-color: #0F172A !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    color: #F8FAFC !important;
}

input:focus, textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
}

/* File Uploader Dropzone */
[data-testid="stFileUploader"] section {
    background-color: #0D1526 !important;
    border: 2px dashed rgba(59, 130, 246, 0.35) !important;
    border-radius: 12px !important;
    padding: 2rem 1.5rem !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: #3B82F6 !important;
    background-color: rgba(13, 21, 38, 0.9) !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #0F172A !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-weight: 600 !important;
}

div[data-testid="stExpander"] {
    border: none !important;
    margin-bottom: 0.75rem !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px 6px 0 0;
    padding: 0.6rem 1.2rem;
    color: #94A3B8;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    color: #38BDF8 !important;
    border-bottom: 2px solid #38BDF8 !important;
    font-weight: 600;
}

/* Citations Box */
.citation-box {
    background: linear-gradient(180deg, #0F172A 0%, #0B1120 100%);
    border-left: 3px solid #3B82F6;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    padding: 0.85rem 1.1rem;
    margin-top: 0.5rem;
    font-size: 0.86rem;
    color: #CBD5E1;
    line-height: 1.55;
}

/* Empty State Box */
.empty-state {
    text-align: center;
    padding: 3.5rem 2rem;
    background: radial-gradient(100% 100% at 50% 50%, #0F172A 0%, #070B14 100%);
    border: 1px dashed rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    margin: 1.75rem 0;
}

.empty-state h3 {
    color: #F8FAFC;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.empty-state p {
    color: #94A3B8;
    font-size: 0.92rem;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.5;
}
</style>
"""

def apply_custom_theme():
    """Injects high-end SaaS styling into the active Streamlit page."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_sidebar_branding(stats: dict):
    """Renders a polished, cohesive sidebar header and live metric chips."""
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand-card">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
                <div style="background: #2563EB; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: bold; color: white;">📄</div>
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF; letter-spacing: -0.02em;">{APP_NAME}</div>
                    <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">RAG KNOWLEDGE CORE</div>
                </div>
            </div>
            <div style="margin-top: 0.85rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                <div class="sidebar-stat-chip">
                    <span style="color: #94A3B8;">Indexed Docs</span>
                    <span class="sidebar-stat-val">{stats.get('total_documents', 0)}</span>
                </div>
                <div class="sidebar-stat-chip">
                    <span style="color: #94A3B8;">Total Words</span>
                    <span class="sidebar-stat-val">{stats.get('total_words', 0):,}</span>
                </div>
                <div class="sidebar-stat-chip">
                    <span style="color: #94A3B8;">Questions Asked</span>
                    <span class="sidebar-stat-val">{stats.get('total_questions', 0)}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_header(title: str, subtitle: str = ""):
    """Renders the top hero card with gradient accents and tag chips."""
    st.markdown(
        f"""
        <div class="askfile-hero">
            <div class="askfile-hero-badge">
                <span style="display:inline-block; width:6px; height:6px; background:#60A5FA; border-radius:50%;"></span>
                AI-Powered Document Intelligence
            </div>
            <h1>{title}</h1>
            <p>{subtitle or APP_SUBTITLE}</p>
            <div class="askfile-hero-tags">
                <span class="askfile-hero-tag">⚡ Local FAISS Vector Search</span>
                <span class="askfile-hero-tag">🛡️ Zero-Hallucination Citations</span>
                <span class="askfile-hero-tag">📄 PDF • Word DOCX • TXT</span>
                <span class="askfile-hero-tag">🔒 100% Private Local Storage</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_metric_card(label: str, value: str, subtext: str = ""):
    """Renders a styled metric card."""
    st.markdown(
        f"""
        <div class="askfile-metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-subtext">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_empty_state(title: str, message: str):
    """Renders a styled placeholder for empty collections."""
    st.markdown(
        f"""
        <div class="empty-state">
            <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">📁</div>
            <h3>{title}</h3>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
