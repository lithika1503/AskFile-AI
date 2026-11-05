"""Configurable text chunking preserving document ID, page numbers, and context."""

import re
from typing import List, Tuple
from database.models import DocumentChunk
from config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class TextChunker:
    """
    Splits document text into overlapping chunks, maintaining page references
    and semantic paragraph/sentence boundaries.
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ):
        if chunk_overlap >= chunk_size:
            chunk_overlap = max(0, chunk_size - 50)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document_id: str,
        pages_content: List[Tuple[int, str]]
    ) -> List[DocumentChunk]:
        """
        Chunks a list of (page_number, page_text) tuples.
        Returns a list of DocumentChunk instances with preserved metadata.
        """
        chunks: List[DocumentChunk] = []
        global_chunk_idx = 0

        for page_num, page_text in pages_content:
            if not page_text or not page_text.strip():
                continue

            page_chunks = self._split_text(page_text)
            for chunk_str in page_chunks:
                if chunk_str.strip():
                    chunk_obj = DocumentChunk(
                        document_id=document_id,
                        chunk_index=global_chunk_idx,
                        page_number=page_num,
                        chunk_text=chunk_str.strip(),
                        embedding_reference=f"{document_id}_{global_chunk_idx}"
                    )
                    chunks.append(chunk_obj)
                    global_chunk_idx += 1

        return chunks

    def _split_text(self, text: str) -> List[str]:
        """
        Splits text by double newlines (paragraphs), then sentences, then words,
        respecting chunk_size and chunk_overlap.
        """
        if len(text) <= self.chunk_size:
            return [text]

        # Break text into paragraphs first
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        pieces: List[str] = []

        for para in paragraphs:
            if len(para) <= self.chunk_size:
                pieces.append(para)
            else:
                # Break large paragraph into sentences
                sentences = re.split(r"(?<=[.!?]) +", para)
                for sent in sentences:
                    if len(sent) <= self.chunk_size:
                        pieces.append(sent)
                    else:
                        # Break large sentence into words
                        words = sent.split(" ")
                        current_word_chunk: List[str] = []
                        current_len = 0
                        for w in words:
                            if current_len + len(w) + 1 > self.chunk_size:
                                if current_word_chunk:
                                    pieces.append(" ".join(current_word_chunk))
                                current_word_chunk = [w]
                                current_len = len(w)
                            else:
                                current_word_chunk.append(w)
                                current_len += len(w) + 1
                        if current_word_chunk:
                            pieces.append(" ".join(current_word_chunk))

        # Now merge pieces up to chunk_size with chunk_overlap
        result_chunks: List[str] = []
        current_chunk: List[str] = []
        current_length = 0

        for piece in pieces:
            piece_len = len(piece)
            if current_length + piece_len + 2 > self.chunk_size and current_chunk:
                combined = " ".join(current_chunk)
                result_chunks.append(combined)

                # Keep overlap pieces from the tail of current_chunk
                overlap_pieces: List[str] = []
                overlap_len = 0
                for item in reversed(current_chunk):
                    if overlap_len + len(item) + 1 <= self.chunk_overlap:
                        overlap_pieces.insert(0, item)
                        overlap_len += len(item) + 1
                    else:
                        break

                current_chunk = overlap_pieces
                current_length = overlap_len

            current_chunk.append(piece)
            current_length += piece_len + 1

        if current_chunk:
            result_chunks.append(" ".join(current_chunk))

        return result_chunks
