"""Database schema migrations and initialization."""

import sqlite3
from pathlib import Path
from config import DATABASE_PATH
from database.connection import get_db
from utils.logging_config import logger

SCHEMA_SQL = """
-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_count INTEGER DEFAULT 1,
    word_count INTEGER DEFAULT 0,
    extracted_text TEXT NOT NULL,
    processing_status TEXT NOT NULL
);

-- Document Chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER DEFAULT 1,
    chunk_text TEXT NOT NULL,
    embedding_reference TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    conversation_title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    message_content TEXT NOT NULL,
    citations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Activity Logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    document_id TEXT,
    activity_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_messages_conv_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_activity_created ON activity_logs(created_at);
"""

def init_db(db_path: Path = DATABASE_PATH) -> None:
    """Initializes SQLite database schema and indexes."""
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
    logger.info(f"Database schema initialized successfully at {db_path}")

if __name__ == "__main__":
    init_db()
