"""
Module 5: AskFile AI Chat (Core RAG Feature)
Source-grounded question answering with multi-document selection, FAISS retrieval,
and verifiable citation cards.
"""

import streamlit as st
import json
from config import APP_NAME
from database.repository import DocumentRepository, AnalyticsRepository
from services.chat_service import ChatService
from services.export_service import ExportService
from utils.ui import apply_custom_theme, render_header, render_empty_state, render_sidebar_branding

st.set_page_config(page_title=f"{APP_NAME} | AI Chat", page_icon="💬", layout="wide")
apply_custom_theme()

stats = AnalyticsRepository.get_overview_stats()
render_sidebar_branding(stats)

render_header("Interactive Document Chat", "Ask questions grounded strictly in your indexed documents with verified page citations")

chat_service = ChatService()

# -------------------------------------------------------------
# Session & Conversation State
# -------------------------------------------------------------
if "conversation_id" not in st.session_state:
    conv = chat_service.get_or_create_conversation()
    st.session_state.conversation_id = conv.id

# -------------------------------------------------------------
# Sidebar: Document Scope & Conversation Actions
# -------------------------------------------------------------
docs = DocumentRepository.get_all()
completed_docs = [d for d in docs if d.processing_status == "completed"]

with st.sidebar:
    st.markdown("### 🎯 Target Documents")
    if not completed_docs:
        st.warning("No processed documents available. Please upload files in Document Upload.")
        selected_doc_ids = []
    else:
        doc_options = {d.id: f"{d.filename} ({d.file_type.upper()})" for d in completed_docs}
        select_all = st.checkbox("Query Across All Documents", value=True)
        if select_all:
            selected_doc_ids = list(doc_options.keys())
            st.caption(f"Searching across {len(selected_doc_ids)} document(s).")
        else:
            selected_doc_ids = st.multiselect(
                "Select specific documents:",
                options=list(doc_options.keys()),
                format_func=lambda x: doc_options[x],
                default=list(doc_options.keys())[:1]
            )

    st.markdown("---")
    st.markdown("### ⚙️ Chat Options")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        # Create a fresh conversation
        new_conv = chat_service.get_or_create_conversation(title="Fresh Session")
        st.session_state.conversation_id = new_conv.id
        st.rerun()

    # Download chat history
    active_msgs = chat_service.get_messages(st.session_state.conversation_id)
    if active_msgs:
        txt_bytes = ExportService.export_chat_txt(active_msgs, "AskFile AI Chat")
        st.download_button(
            label="📥 Download Chat (TXT)",
            data=txt_bytes,
            file_name="askfile_chat.txt",
            mime="text/plain",
            use_container_width=True
        )
        pdf_bytes = ExportService.export_chat_pdf(active_msgs, "AskFile AI Chat")
        st.download_button(
            label="📥 Download Chat (PDF)",
            data=pdf_bytes,
            file_name="askfile_chat.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# -------------------------------------------------------------
# Sample Prompts Helper
# -------------------------------------------------------------
with st.expander("💡 Example Questions & Prompts"):
    st.markdown("""
    - What is the primary purpose and scope of this document?
    - Summarize the main objectives and key findings.
    - What are the important dates, timelines, and financial numbers mentioned?
    - Identify the key risks, advantages, and disadvantages discussed.
    - Explain this topic in simple terms with bullet points.
    """)

# -------------------------------------------------------------
# Message History Display
# -------------------------------------------------------------
messages = chat_service.get_messages(st.session_state.conversation_id)

if not messages:
    render_empty_state(
        "Start a Conversation",
        "Select your target documents from the sidebar and type your question below. "
        "Every answer will be strictly derived from your uploaded files."
    )
else:
    for m in messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

            # Render inspectable source citations
            if m.get("citations"):
                with st.expander(f"📚 Inspect Supporting Evidence ({len(m['citations'])} source passages)"):
                    for c in m["citations"]:
                        st.markdown(
                            f"""
                            <div class="citation-box">
                                <b>Source #{c.get('source_index', 1)}</b> — File: <code>{c.get('filename')}</code> (Page {c.get('page_number', 1)}) | Relevance: <code>{c.get('score', 0):.2f}</code><br>
                                <i>"{c.get('excerpt', '')}"</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# -------------------------------------------------------------
# Chat Input Bar
# -------------------------------------------------------------
if prompt := st.chat_input("Ask a question about your uploaded documents..."):
    if not completed_docs:
        st.error("Please upload and process at least one document before asking questions.")
    elif not selected_doc_ids:
        st.warning("Please select at least one document from the sidebar to query.")
    else:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching document vectors and formulating grounded response..."):
                response = chat_service.ask(
                    conversation_id=st.session_state.conversation_id,
                    question=prompt,
                    document_ids=selected_doc_ids
                )
                st.markdown(response["answer"])

                if response.get("citations"):
                    with st.expander(f"📚 Inspect Supporting Evidence ({len(response['citations'])} source passages)"):
                        for c in response["citations"]:
                            st.markdown(
                                f"""
                                <div class="citation-box">
                                    <b>Source #{c.get('source_index', 1)}</b> — File: <code>{c.get('filename')}</code> (Page {c.get('page_number', 1)}) | Relevance: <code>{c.get('score', 0):.2f}</code><br>
                                    <i>"{c.get('excerpt', '')}"</i>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
        st.rerun()
