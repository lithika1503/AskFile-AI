"""Repository classes providing clean CRUD operations for database entities."""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from database.connection import get_db
from database.models import Document, DocumentChunk, Conversation, Message, ActivityLog
from utils.logging_config import logger

class DocumentRepository:
    """CRUD operations for documents."""

    @staticmethod
    def insert(doc: Document) -> None:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, filename, file_type, file_hash, file_size,
                    page_count, word_count, extracted_text, processing_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.id, doc.filename, doc.file_type, doc.file_hash, doc.file_size,
                    doc.page_count, doc.word_count, doc.extracted_text, doc.processing_status
                )
            )

    @staticmethod
    def get_by_id(doc_id: str) -> Optional[Document]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if row:
                return Document(**dict(row))
            return None

    @staticmethod
    def get_by_hash(file_hash: str) -> Optional[Document]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM documents WHERE file_hash = ?", (file_hash,)).fetchone()
            if row:
                return Document(**dict(row))
            return None

    @staticmethod
    def get_all() -> List[Document]:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM documents ORDER BY upload_date DESC").fetchall()
            return [Document(**dict(r)) for r in rows]

    @staticmethod
    def update_status(doc_id: str, status: str) -> None:
        with get_db() as conn:
            conn.execute("UPDATE documents SET processing_status = ? WHERE id = ?", (status, doc_id))

    @staticmethod
    def delete(doc_id: str) -> bool:
        with get_db() as conn:
            # Foreign key cascade automatically deletes chunks
            cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            return cursor.rowcount > 0

    @staticmethod
    def count() -> int:
        with get_db() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM documents").fetchone()
            return row["cnt"] if row else 0


class ChunkRepository:
    """CRUD operations for document chunks."""

    @staticmethod
    def insert_bulk(chunks: List[DocumentChunk]) -> None:
        if not chunks:
            return
        with get_db() as conn:
            conn.executemany(
                """
                INSERT INTO document_chunks (
                    document_id, chunk_index, page_number, chunk_text, embedding_reference
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (c.document_id, c.chunk_index, c.page_number, c.chunk_text, c.embedding_reference)
                    for c in chunks
                ]
            )

    @staticmethod
    def get_by_document_id(doc_id: str) -> List[DocumentChunk]:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM document_chunks WHERE document_id = ? ORDER BY chunk_index ASC",
                (doc_id,)
            ).fetchall()
            return [DocumentChunk(**dict(r)) for r in rows]

    @staticmethod
    def delete_by_document_id(doc_id: str) -> None:
        with get_db() as conn:
            conn.execute("DELETE FROM document_chunks WHERE document_id = ?", (doc_id,))


class ConversationRepository:
    """CRUD operations for chat conversations."""

    @staticmethod
    def create(conv: Conversation) -> None:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO conversations (id, conversation_title) VALUES (?, ?)",
                (conv.id, conv.conversation_title)
            )

    @staticmethod
    def get_all() -> List[Conversation]:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM conversations ORDER BY updated_at DESC").fetchall()
            return [Conversation(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(conv_id: str) -> Optional[Conversation]:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
            return Conversation(**dict(row)) if row else None

    @staticmethod
    def update_timestamp(conv_id: str) -> None:
        with get_db() as conn:
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conv_id,)
            )

    @staticmethod
    def delete(conv_id: str) -> None:
        with get_db() as conn:
            conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))


class MessageRepository:
    """CRUD operations for chat messages."""

    @staticmethod
    def insert(msg: Message) -> int:
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (conversation_id, role, message_content, citations)
                VALUES (?, ?, ?, ?)
                """,
                (msg.conversation_id, msg.role, msg.message_content, msg.citations)
            )
            # Update conversation timestamp
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (msg.conversation_id,)
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_conversation(conv_id: str) -> List[Message]:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY id ASC",
                (conv_id,)
            ).fetchall()
            return [Message(**dict(r)) for r in rows]

    @staticmethod
    def count() -> int:
        with get_db() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM messages WHERE role = 'user'").fetchone()
            return row["cnt"] if row else 0


class ActivityRepository:
    """CRUD operations for activity logging."""

    @staticmethod
    def log(activity_type: str, description: str, document_id: Optional[str] = None) -> None:
        try:
            with get_db() as conn:
                conn.execute(
                    """
                    INSERT INTO activity_logs (activity_type, activity_description, document_id)
                    VALUES (?, ?, ?)
                    """,
                    (activity_type, description, document_id)
                )
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")

    @staticmethod
    def get_recent(limit: int = 10) -> List[Dict[str, Any]]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT a.*, d.filename 
                FROM activity_logs a 
                LEFT JOIN documents d ON a.document_id = d.id 
                ORDER BY a.created_at DESC LIMIT ?
                """,
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]


class AnalyticsRepository:
    """Aggregated queries for Dashboard and Analytics modules."""

    @staticmethod
    def get_overview_stats() -> Dict[str, Any]:
        with get_db() as conn:
            total_docs = conn.execute("SELECT COUNT(*) as cnt FROM documents").fetchone()["cnt"]
            processed_docs = conn.execute(
                "SELECT COUNT(*) as cnt FROM documents WHERE processing_status = 'completed'"
            ).fetchone()["cnt"]
            failed_docs = conn.execute(
                "SELECT COUNT(*) as cnt FROM documents WHERE processing_status = 'failed'"
            ).fetchone()["cnt"]
            total_words = conn.execute(
                "SELECT COALESCE(SUM(word_count), 0) as cnt FROM documents"
            ).fetchone()["cnt"]
            total_questions = conn.execute(
                "SELECT COUNT(*) as cnt FROM messages WHERE role = 'user'"
            ).fetchone()["cnt"]
            avg_size = conn.execute(
                "SELECT COALESCE(AVG(file_size), 0) as val FROM documents"
            ).fetchone()["val"]
            avg_words = conn.execute(
                "SELECT COALESCE(AVG(word_count), 0) as val FROM documents"
            ).fetchone()["val"]

            return {
                "total_documents": total_docs,
                "processed_documents": processed_docs,
                "failed_documents": failed_docs,
                "total_words": total_words,
                "total_questions": total_questions,
                "avg_file_size": avg_size,
                "avg_word_count": avg_words,
            }

    @staticmethod
    def get_document_type_distribution() -> List[Dict[str, Any]]:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT file_type, COUNT(*) as count FROM documents GROUP BY file_type"
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_processing_status_distribution() -> List[Dict[str, Any]]:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT processing_status, COUNT(*) as count FROM documents GROUP BY processing_status"
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_uploads_over_time() -> List[Dict[str, Any]]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT DATE(upload_date) as upload_day, COUNT(*) as count 
                FROM documents 
                GROUP BY DATE(upload_date) 
                ORDER BY upload_day ASC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_activity_breakdown() -> List[Dict[str, Any]]:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT activity_type, COUNT(*) as count 
                FROM activity_logs 
                GROUP BY activity_type 
                ORDER BY count DESC
                """
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_recent(limit: int = 10) -> List[Dict[str, Any]]:
        """Delegates to ActivityRepository to retrieve recent audit logs."""
        return ActivityRepository.get_recent(limit)

    @staticmethod
    def clear_all_history() -> None:
        """Purges messages and conversations, resets activity logs."""
        with get_db() as conn:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM activity_logs")
