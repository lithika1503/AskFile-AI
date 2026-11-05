"""Service managing chat sessions, conversational turns, RAG queries, and citation tracking."""

import uuid
import json
from typing import List, Dict, Any, Optional
from database.models import Conversation, Message
from database.repository import (
    ConversationRepository,
    MessageRepository,
    ActivityRepository
)
from core.rag_pipeline import RAGPipeline
from utils.constants import ACTIVITY_CHAT, ROLE_USER, ROLE_ASSISTANT
from utils.logging_config import logger

class ChatService:
    """Manages chat session lifecycle, prompt assembly, and message persistence."""

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        self.rag = rag_pipeline or RAGPipeline()

    def get_or_create_conversation(self, conv_id: Optional[str] = None, title: str = "New Conversation") -> Conversation:
        """Retrieves an existing conversation or creates a new one."""
        if conv_id:
            conv = ConversationRepository.get_by_id(conv_id)
            if conv:
                return conv

        new_id = conv_id or str(uuid.uuid4())
        conv = Conversation(id=new_id, conversation_title=title)
        ConversationRepository.create(conv)
        return conv

    def get_messages(self, conv_id: str) -> List[Dict[str, Any]]:
        """Retrieves and deserializes all messages for a conversation."""
        msgs = MessageRepository.get_by_conversation(conv_id)
        result = []
        for m in msgs:
            citations_data = []
            if m.citations:
                try:
                    citations_data = json.loads(m.citations)
                except Exception:
                    citations_data = []
            result.append({
                "id": m.id,
                "role": m.role,
                "content": m.message_content,
                "citations": citations_data,
                "created_at": m.created_at
            })
        return result

    def ask(
        self,
        conversation_id: str,
        question: str,
        document_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Processes a user question:
        - Saves user message.
        - Gathers conversation history.
        - Invokes RAG pipeline.
        - Saves assistant response with serialized citations.
        - Returns answer and citations.
        """
        # Save user message
        user_msg = Message(
            conversation_id=conversation_id,
            role=ROLE_USER,
            message_content=question
        )
        MessageRepository.insert(user_msg)

        # Retrieve prior turns for conversational context
        existing_messages = self.get_messages(conversation_id)
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in existing_messages[:-1]  # Exclude current question
        ]

        # Execute RAG
        rag_output = self.rag.answer_question(
            question=question,
            document_ids=document_ids,
            conversation_history=history
        )

        answer = rag_output["answer"]
        citations = rag_output["citations"]

        # Save assistant response
        assistant_msg = Message(
            conversation_id=conversation_id,
            role=ROLE_ASSISTANT,
            message_content=answer,
            citations=json.dumps(citations, ensure_ascii=False) if citations else None
        )
        MessageRepository.insert(assistant_msg)

        # Log activity
        doc_count = len(document_ids) if document_ids else "all"
        ActivityRepository.log(
            ACTIVITY_CHAT,
            f"Asked question: '{question[:50]}...' across {doc_count} document(s)"
        )

        return {
            "answer": answer,
            "citations": citations,
            "retrieved_chunks": rag_output.get("retrieved_chunks", [])
        }
