"""Data models and schemas for SQLite entities."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class Document:
    id: str
    filename: str
    file_type: str
    file_hash: str
    file_size: int
    extracted_text: str
    processing_status: str
    page_count: int = 1
    word_count: int = 0
    upload_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "extracted_text": self.extracted_text,
            "processing_status": self.processing_status,
            "upload_date": self.upload_date,
        }

@dataclass
class DocumentChunk:
    document_id: str
    chunk_index: int
    chunk_text: str
    page_number: int = 1
    embedding_reference: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "chunk_index": self.chunk_index,
            "page_number": self.page_number,
            "chunk_text": self.chunk_text,
            "embedding_reference": self.embedding_reference,
        }

@dataclass
class Conversation:
    id: str
    conversation_title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class Message:
    conversation_id: str
    role: str
    message_content: str
    citations: Optional[str] = None  # JSON serialized citations
    id: Optional[int] = None
    created_at: Optional[str] = None

@dataclass
class ActivityLog:
    activity_type: str
    activity_description: str
    document_id: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
