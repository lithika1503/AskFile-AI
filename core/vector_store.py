"""FAISS vector store with persistent storage and document-level filtering."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import faiss
import numpy as np

from config import VECTOR_DB_DIR
from database.models import DocumentChunk
from utils.logging_config import logger

INDEX_FILE = VECTOR_DB_DIR / "faiss_index.bin"
METADATA_FILE = VECTOR_DB_DIR / "index_metadata.json"

class VectorStore:
    """
    Manages FAISS vector indexing, persistent disk saving, document filtering,
    and metadata association.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self._load_or_create()

    def _load_or_create(self) -> None:
        """Loads existing FAISS index and metadata from disk, or initializes a new one."""
        if INDEX_FILE.exists() and METADATA_FILE.exists():
            try:
                self.index = faiss.read_index(str(INDEX_FILE))
                with open(METADATA_FILE, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors.")
                return
            except Exception as e:
                logger.error(f"Failed to load FAISS index from disk: {e}. Reinitializing...")

        # Create IndexFlatIP (Inner Product = Cosine Similarity for normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._save()

    def _save(self) -> None:
        """Persists the index and metadata to disk."""
        try:
            VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
            if self.index is not None:
                faiss.write_index(self.index, str(INDEX_FILE))
            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error persisting vector store: {e}")

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: np.ndarray,
        filename: str = ""
    ) -> None:
        """
        Adds chunk vectors and metadata to the FAISS index and persists to disk.
        """
        if len(chunks) == 0 or embeddings.shape[0] == 0:
            return

        if embeddings.shape[1] != self.dimension:
            # Reinitialize index if dimension changed
            self.dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

        # Ensure embeddings are normalized float32
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)

        for chunk in chunks:
            self.metadata.append({
                "document_id": chunk.document_id,
                "filename": filename,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "chunk_text": chunk.chunk_text,
                "embedding_reference": chunk.embedding_reference
            })

        self._save()
        logger.info(f"Added {len(chunks)} vectors to FAISS. Total index count: {self.index.ntotal}")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 4,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches the index for most similar chunks.
        Supports document_ids filtering to prevent cross-contamination.
        Returns list of dicts with chunk metadata and similarity score.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        # Reshape query embedding
        q_vec = query_embedding.reshape(1, -1).astype("float32")
        faiss.normalize_L2(q_vec)

        # Retrieve a broader candidate pool if filtering by documents
        pool_k = min(self.index.ntotal, top_k * 5 if document_ids else top_k)
        scores, indices = self.index.search(q_vec, pool_k)

        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]

            # Document filtering
            if document_ids and meta["document_id"] not in document_ids:
                continue

            results.append({
                "document_id": meta["document_id"],
                "filename": meta.get("filename", ""),
                "chunk_index": meta["chunk_index"],
                "page_number": meta["page_number"],
                "chunk_text": meta["chunk_text"],
                "score": float(np.clip(score, 0.0, 1.0))
            })

            if len(results) >= top_k:
                break

        return results

    def delete_document_vectors(self, document_id: str) -> None:
        """
        Deletes all vectors and metadata associated with document_id,
        then rebuilds the FAISS index to ensure clean state.
        """
        if not self.metadata:
            return

        # Identify items to keep
        keep_indices = [
            i for i, item in enumerate(self.metadata)
            if item["document_id"] != document_id
        ]

        if len(keep_indices) == len(self.metadata):
            return  # No vectors to remove

        logger.info(f"Removing vectors for document {document_id}. Kept {len(keep_indices)} vectors.")

        if not keep_indices:
            # All removed
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
            self._save()
            return

        # Reconstruct vectors for remaining items
        remaining_vectors = np.empty((len(keep_indices), self.dimension), dtype="float32")
        for new_idx, old_idx in enumerate(keep_indices):
            remaining_vectors[new_idx] = self.index.reconstruct(int(old_idx))

        new_index = faiss.IndexFlatIP(self.dimension)
        faiss.normalize_L2(remaining_vectors)
        new_index.add(remaining_vectors)

        self.index = new_index
        self.metadata = [self.metadata[i] for i in keep_indices]
        self._save()

    def reset(self) -> None:
        """Clears all vectors and metadata from memory and disk."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        if INDEX_FILE.exists():
            INDEX_FILE.unlink()
        if METADATA_FILE.exists():
            METADATA_FILE.unlink()
        logger.info("Vector store reset successfully.")
