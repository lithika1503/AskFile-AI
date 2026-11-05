"""Tests for SQLite database operations and repositories."""

import pytest
import uuid
from database.migrations import init_db
from database.models import Document, DocumentChunk, Conversation, Message
from database.repository import (
    DocumentRepository,
    ChunkRepository,
    ConversationRepository,
    MessageRepository,
    AnalyticsRepository
)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_document_crud():
    doc_id = str(uuid.uuid4())
    doc_hash = str(uuid.uuid4())
    
    doc = Document(
        id=doc_id,
        filename="test_manual.pdf",
        file_type="pdf",
        file_hash=doc_hash,
        file_size=1024,
        page_count=2,
        word_count=150,
        extracted_text="This is test content for document CRUD operations.",
        processing_status="completed"
    )
    
    # Insert
    DocumentRepository.insert(doc)
    
    # Retrieve by ID
    retrieved = DocumentRepository.get_by_id(doc_id)
    assert retrieved is not None
    assert retrieved.filename == "test_manual.pdf"
    assert retrieved.word_count == 150
    
    # Retrieve by Hash
    retrieved_hash = DocumentRepository.get_by_hash(doc_hash)
    assert retrieved_hash is not None
    assert retrieved_hash.id == doc_id
    
    # Add Chunks
    chunk1 = DocumentChunk(document_id=doc_id, chunk_index=0, page_number=1, chunk_text="Chunk one")
    chunk2 = DocumentChunk(document_id=doc_id, chunk_index=1, page_number=2, chunk_text="Chunk two")
    ChunkRepository.insert_bulk([chunk1, chunk2])
    
    chunks = ChunkRepository.get_by_document_id(doc_id)
    assert len(chunks) == 2
    
    # Delete Document and verify cascade
    deleted = DocumentRepository.delete(doc_id)
    assert deleted is True
    assert DocumentRepository.get_by_id(doc_id) is None
    assert len(ChunkRepository.get_by_document_id(doc_id)) == 0

def test_conversation_and_messages():
    conv_id = str(uuid.uuid4())
    conv = Conversation(id=conv_id, conversation_title="Unit Test Conversation")
    ConversationRepository.create(conv)
    
    user_msg = Message(
        conversation_id=conv_id,
        role="user",
        message_content="Hello, what is the document about?"
    )
    msg_id = MessageRepository.insert(user_msg)
    assert msg_id > 0
    
    messages = MessageRepository.get_by_conversation(conv_id)
    assert len(messages) == 1
    assert messages[0].message_content == "Hello, what is the document about?"
    
    ConversationRepository.delete(conv_id)
    assert ConversationRepository.get_by_id(conv_id) is None

def test_activity_and_analytics_get_recent():
    from database.repository import ActivityRepository, AnalyticsRepository
    ActivityRepository.log("TEST_EVENT", "Sample activity description for test")
    
    # Test ActivityRepository.get_recent
    recent_act = ActivityRepository.get_recent(5)
    assert isinstance(recent_act, list)
    assert len(recent_act) >= 1
    assert any(a["activity_type"] == "TEST_EVENT" for a in recent_act)
    
    # Test AnalyticsRepository.get_recent compatible method
    recent_an = AnalyticsRepository.get_recent(5)
    assert isinstance(recent_an, list)
    assert len(recent_an) >= 1
    assert any(a["activity_type"] == "TEST_EVENT" for a in recent_an)
