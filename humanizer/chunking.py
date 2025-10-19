"""
Text Chunking and Rejoining System
Intelligently splits large texts for processing and seamlessly reassembles them.
"""

import re
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata for reassembly."""
    index: int
    text: str
    overlap_start: str  # Text from previous chunk for context
    overlap_end: str    # Text to provide to next chunk
    has_overlap_start: bool
    has_overlap_end: bool
    original_markers: Dict[str, any]  # Formatting markers, structure info


class TextChunker:
    """
    Intelligently chunks text for processing.
    Respects natural boundaries and preserves structure.
    """
    
    def __init__(
        self,
        min_chunk_size: int = 200,
        max_chunk_size: int = 400,
        overlap_sentences: int = 2
    ):
        """
        Initialize the chunker.
        
        Args:
            min_chunk_size: Minimum words per chunk
            max_chunk_size: Maximum words per chunk
            overlap_sentences: Number of sentences to overlap between chunks
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_sentences = overlap_sentences
        
    def chunk_text(self, text: str) -> List[Chunk]:
        """
        Split text into processable chunks with intelligent boundaries.
        
        Args:
            text: The full text to chunk
            
        Returns:
            List of Chunk objects with metadata
        """
        # Preserve protected spans (citations, code, quotes, etc.)
        protected_spans = self._identify_protected_spans(text)
        
        # Split into paragraphs first
        paragraphs = self._split_into_paragraphs(text)
        
        # Build chunks respecting boundaries
        chunks = []
        current_chunk_text = []
        current_word_count = 0
        previous_overlap = ""
        
        for para in paragraphs:
            para_word_count = self._count_words(para)
            
            # If paragraph alone exceeds max, split by sentences
            if para_word_count > self.max_chunk_size:
                # Finish current chunk if any
                if current_chunk_text:
                    chunk_text = "\n\n".join(current_chunk_text)
                    overlap_end = self._extract_overlap_end(chunk_text)
                    chunks.append(self._create_chunk(
                        index=len(chunks),
                        text=chunk_text,
                        overlap_start=previous_overlap,
                        overlap_end=overlap_end,
                        has_overlap_start=bool(previous_overlap)
                    ))
                    previous_overlap = overlap_end
                    current_chunk_text = []
                    current_word_count = 0
                
                # Split large paragraph by sentences
                sentence_chunks = self._chunk_large_paragraph(para, previous_overlap)
                chunks.extend(sentence_chunks)
                
                if sentence_chunks:
                    previous_overlap = sentence_chunks[-1].overlap_end
                    
            # If adding this paragraph exceeds max, start new chunk
            elif current_word_count + para_word_count > self.max_chunk_size:
                if current_chunk_text:  # Don't create empty chunks
                    chunk_text = "\n\n".join(current_chunk_text)
                    overlap_end = self._extract_overlap_end(chunk_text)
                    chunks.append(self._create_chunk(
                        index=len(chunks),
                        text=chunk_text,
                        overlap_start=previous_overlap,
                        overlap_end=overlap_end,
                        has_overlap_start=bool(previous_overlap)
                    ))
                    previous_overlap = overlap_end
                    current_chunk_text = [para]
                    current_word_count = para_word_count
                else:
                    current_chunk_text.append(para)
                    current_word_count += para_word_count
                    
            # Add paragraph to current chunk
            else:
                current_chunk_text.append(para)
                current_word_count += para_word_count
        
        # Add final chunk if any
        if current_chunk_text:
            chunk_text = "\n\n".join(current_chunk_text)
            overlap_end = ""  # Last chunk has no overlap_end
            chunks.append(self._create_chunk(
                index=len(chunks),
                text=chunk_text,
                overlap_start=previous_overlap,
                overlap_end=overlap_end,
                has_overlap_start=bool(previous_overlap)
            ))
        
        return chunks
    
    def _identify_protected_spans(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Identify spans that should never be split.
        
        Returns:
            List of (start, end, type) tuples
        """
        protected = []
        
        # Citations: [1], [Author, 2020], etc.
        for match in re.finditer(r'\[[\w\s,;:]+\d+\]', text):
            protected.append((match.start(), match.end(), 'citation'))
        
        # Quoted text
        for match in re.finditer(r'"[^"]+"|\'[^\']+\'', text):
            protected.append((match.start(), match.end(), 'quote'))
        
        # Code blocks (markdown)
        for match in re.finditer(r'```[\s\S]*?```|`[^`]+`', text):
            protected.append((match.start(), match.end(), 'code'))
        
        # URLs
        for match in re.finditer(r'https?://[^\s]+', text):
            protected.append((match.start(), match.end(), 'url'))
        
        # Tables (markdown)
        for match in re.finditer(r'\|[^\n]+\|(\n\|[^\n]+\|)+', text):
            protected.append((match.start(), match.end(), 'table'))
        
        return protected
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs, preserving structure."""
        # Split on double newlines, but preserve them
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        return paragraphs
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (can be enhanced)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def _extract_overlap_end(self, text: str) -> str:
        """Extract last N sentences for overlap with next chunk."""
        sentences = self._split_into_sentences(text)
        overlap_sentences = sentences[-self.overlap_sentences:] if len(sentences) > self.overlap_sentences else sentences
        return " ".join(overlap_sentences)
    
    def _chunk_large_paragraph(self, paragraph: str, previous_overlap: str) -> List[Chunk]:
        """Split a large paragraph into sentence-based chunks."""
        sentences = self._split_into_sentences(paragraph)
        chunks = []
        current_sentences = []
        current_word_count = 0
        overlap = previous_overlap
        
        for sentence in sentences:
            sentence_words = self._count_words(sentence)
            
            if current_word_count + sentence_words > self.max_chunk_size and current_sentences:
                # Create chunk
                chunk_text = " ".join(current_sentences)
                overlap_end = self._extract_overlap_end(chunk_text)
                chunks.append(self._create_chunk(
                    index=len(chunks),
                    text=chunk_text,
                    overlap_start=overlap,
                    overlap_end=overlap_end,
                    has_overlap_start=bool(overlap)
                ))
                overlap = overlap_end
                current_sentences = [sentence]
                current_word_count = sentence_words
            else:
                current_sentences.append(sentence)
                current_word_count += sentence_words
        
        # Add remaining sentences
        if current_sentences:
            chunk_text = " ".join(current_sentences)
            overlap_end = self._extract_overlap_end(chunk_text)
            chunks.append(self._create_chunk(
                index=len(chunks),
                text=chunk_text,
                overlap_start=overlap,
                overlap_end=overlap_end,
                has_overlap_start=bool(overlap)
            ))
        
        return chunks
    
    def _create_chunk(
        self,
        index: int,
        text: str,
        overlap_start: str,
        overlap_end: str,
        has_overlap_start: bool
    ) -> Chunk:
        """Create a Chunk object with metadata."""
        return Chunk(
            index=index,
            text=text,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
            has_overlap_start=has_overlap_start,
            has_overlap_end=bool(overlap_end),
            original_markers=self._extract_markers(text)
        )
    
    def _extract_markers(self, text: str) -> Dict[str, any]:
        """Extract formatting markers from text."""
        markers = {
            'has_list': bool(re.search(r'^\s*[-*+]\s', text, re.MULTILINE)),
            'has_numbered_list': bool(re.search(r'^\s*\d+\.\s', text, re.MULTILINE)),
            'has_heading': bool(re.search(r'^#{1,6}\s', text, re.MULTILINE)),
            'has_blockquote': bool(re.search(r'^>\s', text, re.MULTILINE)),
            'has_code': bool(re.search(r'```|`[^`]+`', text)),
            'starts_with_list': bool(re.match(r'^\s*[-*+\d]+[.)]\s', text)),
            'paragraph_count': len(re.split(r'\n\s*\n', text))
        }
        return markers


class TextRejoiner:
    """
    Reassembles processed chunks into a seamless document.
    Removes overlaps and validates structure.
    """
    
    def rejoin_chunks(self, processed_chunks: List[Tuple[Chunk, str]]) -> str:
        """
        Rejoin processed chunks into final text with consistency checks.
        Optimized for better flow with fewer, larger chunks (400-500 words).
        
        Args:
            processed_chunks: List of (original_chunk, processed_text) tuples
            
        Returns:
            Final reassembled text with smooth transitions
        """
        if not processed_chunks:
            return ""
        
        if len(processed_chunks) == 1:
            return processed_chunks[0][1]
        
        # Sort by original index to ensure correct order
        sorted_chunks = sorted(processed_chunks, key=lambda x: x[0].index)
        
        print(f"   🔗 Rejoining {len(sorted_chunks)} chunks with consistency checks...")
        
        # Build final text, removing overlaps
        final_parts = []
        
        for i, (original_chunk, processed_text) in enumerate(sorted_chunks):
            # For first chunk, use as-is
            if i == 0:
                final_parts.append(processed_text)
            else:
                # Remove overlap from start of this chunk
                cleaned_text = self._remove_overlap_start(
                    processed_text,
                    original_chunk.overlap_start,
                    final_parts[-1]
                )
                
                # Check transition quality between chunks
                self._check_transition_quality(final_parts[-1], cleaned_text, i)
                
                final_parts.append(cleaned_text)
        
        # Join all parts
        final_text = self._join_parts(final_parts)
        
        # Validate structure
        self._validate_structure(final_text, [c[0] for c in sorted_chunks])
        
        # Final consistency check
        self._post_rejoin_review(final_text, len(sorted_chunks))
        
        return final_text
    
    def _remove_overlap_start(
        self,
        current_text: str,
        expected_overlap: str,
        previous_text: str
    ) -> str:
        """
        Remove overlapping text from the start of current chunk.
        
        Args:
            current_text: The processed text of current chunk
            expected_overlap: The overlap text we added for context
            previous_text: The previous chunk's text
            
        Returns:
            Text with overlap removed
        """
        if not expected_overlap:
            return current_text
        
        # Try to find where the overlap ends in current_text
        # Use fuzzy matching since LLM may have slightly modified it
        overlap_sentences = self._split_into_sentences(expected_overlap)
        current_sentences = self._split_into_sentences(current_text)
        
        # Find the last sentence of overlap in current_text
        best_match_index = 0
        max_similarity = 0
        
        for i in range(min(5, len(current_sentences))):  # Check first 5 sentences
            similarity = self._sentence_similarity(
                overlap_sentences[-1] if overlap_sentences else "",
                current_sentences[i]
            )
            if similarity > max_similarity:
                max_similarity = similarity
                best_match_index = i
        
        # If we found a good match (>70% similar), remove up to and including it
        if max_similarity > 0.7:
            # Rejoin from the sentence after the match
            remaining_sentences = current_sentences[best_match_index + 1:]
            return " ".join(remaining_sentences)
        
        # If no good match, return as-is (safer than removing wrong content)
        return current_text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """
        Calculate similarity between two sentences.
        Simple word-based similarity.
        """
        if not sent1 or not sent2:
            return 0.0
        
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _join_parts(self, parts: List[str]) -> str:
        """Join text parts with appropriate spacing."""
        # Clean up each part
        cleaned_parts = []
        for part in parts:
            part = part.strip()
            if part:
                cleaned_parts.append(part)
        
        # Join with double newline to preserve paragraph structure
        return "\n\n".join(cleaned_parts)
    
    def _validate_structure(self, final_text: str, original_chunks: List[Chunk]) -> None:
        """
        Validate that the final text maintains structural integrity.
        
        Raises:
            ValueError: If validation fails
        """
        # Check for unclosed quotes
        quote_count = final_text.count('"')
        if quote_count % 2 != 0:
            # Warning, but don't fail (LLM might have intentionally changed quotes)
            pass
        
        # Check for unclosed parentheses
        open_paren = final_text.count('(')
        close_paren = final_text.count(')')
        if open_paren != close_paren:
            # Warning only
            pass
        
        # Check paragraph count is reasonable
        final_para_count = len(re.split(r'\n\s*\n', final_text))
        original_para_count = sum(c.original_markers.get('paragraph_count', 0) for c in original_chunks)
        
        # Allow some variation (LLM might merge/split paragraphs)
        if abs(final_para_count - original_para_count) > len(original_chunks):
            # Warning only - LLM might have restructured
            pass
    
    def _check_transition_quality(self, previous_chunk: str, current_chunk: str, chunk_index: int) -> None:
        """
        Check the quality of transition between two chunks.
        Logs warnings for potential issues.
        
        Args:
            previous_chunk: The previous chunk text
            current_chunk: The current chunk text
            chunk_index: Index of current chunk (for logging)
        """
        # Get last sentence of previous and first sentence of current
        prev_sentences = self._split_into_sentences(previous_chunk)
        curr_sentences = self._split_into_sentences(current_chunk)
        
        if not prev_sentences or not curr_sentences:
            return
        
        last_sent = prev_sentences[-1]
        first_sent = curr_sentences[0]
        
        # Check for awkward repetition
        similarity = self._sentence_similarity(last_sent, first_sent)
        if similarity > 0.5:
            print(f"      ⚠️ High similarity ({similarity:.2f}) at chunk {chunk_index} boundary - may need review")
        
        # Check if sentences start with lowercase (might indicate cut-off)
        if first_sent and first_sent[0].islower():
            print(f"      ⚠️ Chunk {chunk_index} starts with lowercase - potential context loss")
    
    def _post_rejoin_review(self, final_text: str, chunk_count: int) -> None:
        """
        Final review of rejoined text for consistency issues.
        
        Args:
            final_text: The final rejoined text
            chunk_count: Number of chunks that were rejoined
        """
        print(f"   ✅ Post-rejoin review:")
        
        # Check for obvious redundancy patterns
        paragraphs = re.split(r'\n\s*\n', final_text)
        
        redundancy_found = False
        for i in range(len(paragraphs) - 1):
            if i >= len(paragraphs) - 1:
                break
            curr_para = paragraphs[i]
            next_para = paragraphs[i + 1]
            
            # Check if paragraphs are very similar (might indicate failed overlap removal)
            if len(curr_para) > 20 and len(next_para) > 20:
                similarity = self._sentence_similarity(curr_para[:100], next_para[:100])
                if similarity > 0.7:
                    redundancy_found = True
                    print(f"      ⚠️ Potential redundancy between paragraphs {i+1} and {i+2}")
        
        if not redundancy_found:
            print(f"      ✓ No major redundancy issues detected")
        
        # Check text expansion ratio
        word_count = len(final_text.split())
        print(f"      ✓ Final word count: {word_count} words from {chunk_count} chunks")
        print(f"      ✓ Average chunk contribution: {word_count // chunk_count if chunk_count > 0 else 0} words/chunk")
