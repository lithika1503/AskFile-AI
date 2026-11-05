"""Service managing file uploads, processing pipeline, deduplication, and storage."""

import uuid
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from config import UPLOADS_DIR
from database.models import Document, DocumentChunk
from database.repository import DocumentRepository, ChunkRepository, ActivityRepository
from core.document_processor import DocumentProcessor
from core.text_chunker import TextChunker
from core.embedding_engine import EmbeddingEngine
from core.vector_store import VectorStore
from utils.constants import (
    ACTIVITY_UPLOAD,
    ACTIVITY_PROCESS,
    ACTIVITY_DELETE,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PROCESSING
)
from utils.helpers import compute_file_hash, sanitize_filename
from utils.validators import validate_uploaded_file
from utils.logging_config import logger

class UploadService:
    """Orchestrates file upload validation, text extraction, vectorization, and storage."""

    def __init__(
        self,
        embedding_engine: Optional[EmbeddingEngine] = None,
        vector_store: Optional[VectorStore] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        self.embedding_engine = embedding_engine or EmbeddingEngine()
        self.vector_store = vector_store or VectorStore(self.embedding_engine.get_dimension())
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process_upload(
        self,
        filename: str,
        file_bytes: bytes,
        file_size: int
    ) -> Tuple[bool, str, Optional[Document]]:
        """
        Validates, saves, extracts, embeds, and indexes an uploaded file.
        Returns (success, message_or_error, document_object).
        """
        sanitized_name = sanitize_filename(filename)

        # 1. Validation
        is_valid, err_msg = validate_uploaded_file(sanitized_name, file_size, file_bytes)
        if not is_valid:
            return False, err_msg or "Validation failed.", None

        # 2. Duplicate Detection via SHA-256 Hash
        file_hash = compute_file_hash(file_bytes)
        existing_doc = DocumentRepository.get_by_hash(file_hash)
        if existing_doc:
            return False, f"Duplicate document: '{sanitized_name}' has already been uploaded as '{existing_doc.filename}'.", existing_doc

        doc_id = str(uuid.uuid4())
        _, ext = os.path.splitext(sanitized_name.lower())
        file_type = ext.lstrip(".")

        # 3. Secure file storage (Internal path, never exposed to user)
        stored_path = UPLOADS_DIR / f"{doc_id}{ext}"
        try:
            with open(stored_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            logger.error(f"Failed to write file to storage: {e}")
            return False, "Failed to save file to server storage.", None

        # 4. Text Extraction
        try:
            extraction = DocumentProcessor.process_file(sanitized_name, file_bytes)
        except Exception as extract_err:
            logger.error(f"Extraction failed for {sanitized_name}: {extract_err}")
            # Insert as failed
            failed_doc = Document(
                id=doc_id,
                filename=sanitized_name,
                file_type=file_type,
                file_hash=file_hash,
                file_size=file_size,
                extracted_text="",
                processing_status=STATUS_FAILED,
                page_count=1,
                word_count=0
            )
            DocumentRepository.insert(failed_doc)
            ActivityRepository.log(ACTIVITY_UPLOAD, f"Uploaded '{sanitized_name}' (Processing Failed: {str(extract_err)})", doc_id)
            return False, f"Document processing failed: {str(extract_err)}", failed_doc

        # 5. Text Chunking
        chunks = self.chunker.chunk_document(
            document_id=doc_id,
            pages_content=extraction.pages_content
        )

        # 6. Embedding Generation & Vector Indexing
        if chunks:
            chunk_texts = [c.chunk_text for c in chunks]
            embeddings = self.embedding_engine.embed_texts(chunk_texts)
            self.vector_store.add_chunks(chunks, embeddings, filename=sanitized_name)

        # 7. Database Persistence
        doc = Document(
            id=doc_id,
            filename=sanitized_name,
            file_type=file_type,
            file_hash=file_hash,
            file_size=file_size,
            extracted_text=extraction.full_text,
            processing_status=STATUS_COMPLETED,
            page_count=extraction.total_pages,
            word_count=extraction.word_count
        )
        DocumentRepository.insert(doc)
        ChunkRepository.insert_bulk(chunks)

        # 8. Activity Logging
        ActivityRepository.log(ACTIVITY_UPLOAD, f"Uploaded document '{sanitized_name}' ({doc.word_count} words)", doc_id)
        ActivityRepository.log(ACTIVITY_PROCESS, f"Successfully processed {len(chunks)} chunks into vector index", doc_id)

        msg = f"Document '{sanitized_name}' processed successfully ({len(chunks)} chunks, {extraction.word_count} words)."
        if extraction.warning:
            msg += f" Note: {extraction.warning}"

        return True, msg, doc

    def reprocess_document(self, doc_id: str) -> Tuple[bool, str]:
        """Reprocesses a failed or existing document from stored file."""
        doc = DocumentRepository.get_by_id(doc_id)
        if not doc:
            return False, "Document not found in database."

        # Find stored file
        candidates = list(UPLOADS_DIR.glob(f"{doc_id}.*"))
        if not candidates:
            return False, "Original file is missing from storage."

        file_path = candidates[0]
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            extraction = DocumentProcessor.process_file(doc.filename, file_bytes)
            chunks = self.chunker.chunk_document(doc_id, extraction.pages_content)

            # Re-index vectors
            self.vector_store.delete_document_vectors(doc_id)
            if chunks:
                embeddings = self.embedding_engine.embed_texts([c.chunk_text for c in chunks])
                self.vector_store.add_chunks(chunks, embeddings, filename=doc.filename)

            # Update DB
            ChunkRepository.delete_by_document_id(doc_id)
            ChunkRepository.insert_bulk(chunks)
            DocumentRepository.update_status(doc_id, STATUS_COMPLETED)

            # Update word/page counts
            with open(file_path, "rb"):
                pass  # verified
            ActivityRepository.log(ACTIVITY_PROCESS, f"Reprocessed document '{doc.filename}'", doc_id)
            return True, f"Document '{doc.filename}' reprocessed successfully."

        except Exception as e:
            logger.error(f"Reprocessing error for {doc_id}: {e}")
            return False, f"Reprocessing failed: {str(e)}"

    def delete_document(self, doc_id: str) -> Tuple[bool, str]:
        """Completely deletes a document, its chunks, its vectors, and its uploaded binary."""
        doc = DocumentRepository.get_by_id(doc_id)
        if not doc:
            return False, "Document not found."

        # 1. Remove vectors
        self.vector_store.delete_document_vectors(doc_id)

        # 2. Remove DB records (CASCADE deletes chunks)
        DocumentRepository.delete(doc_id)

        # 3. Remove physical file
        for f in UPLOADS_DIR.glob(f"{doc_id}.*"):
            try:
                f.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete stored file {f}: {e}")

        ActivityRepository.log(ACTIVITY_DELETE, f"Deleted document '{doc.filename}'", doc_id)
        return True, f"Document '{doc.filename}' and its vector embeddings deleted successfully."
