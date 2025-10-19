# Chunking and Rejoining Pipeline Documentation

## Overview

The chunking system intelligently splits large texts (up to ~2000 words) for processing and seamlessly reassembles them without any post-processing LLM pass.

## Architecture

```
Input Text (up to 2000 words)
         │
         ▼
    ┌─────────────────────┐
    │   Word Count Check  │
    │   < 500 words?      │
    └─────────┬───────────┘
              │
         ┌────┴────┐
         │         │
      YES│         │NO
         │         │
         ▼         ▼
    ┌────────┐  ┌──────────────────┐
    │ Direct │  │  Text Chunker    │
    │Process │  │  (chunking.py)   │
    └────────┘  └────────┬─────────┘
         │               │
         │          Splits into chunks
         │          (200-400 words each)
         │               │
         │               ▼
         │      ┌─────────────────────┐
         │      │ Process Each Chunk  │
         │      │ via LLM Engine      │
         │      └─────────┬───────────┘
         │                │
         │                ▼
         │       ┌─────────────────────┐
         │       │   Text Rejoiner     │
         │       │  (chunking.py)      │
         │       │  • Remove overlaps  │
         │       │  • Validate         │
         │       └─────────┬───────────┘
         │                 │
         └─────────────────┘
                   │
                   ▼
          Final Humanized Text
```

## Key Components

### 1. TextChunker Class

**Purpose**: Intelligently split text into processable chunks.

**Features**:
- Respects natural boundaries (sentences, paragraphs)
- Never splits protected spans (citations, quotes, code, tables, lists)
- Adds configurable overlap between chunks for context
- Preserves formatting markers (Markdown, lists, headings)

**Configuration**:
```python
chunker = TextChunker(
    min_chunk_size=200,     # Minimum words per chunk
    max_chunk_size=400,     # Maximum words per chunk
    overlap_sentences=2     # Sentences to overlap between chunks
)
```

**Protected Spans**:
- Citations: `[1]`, `[Author, 2020]`
- Quotes: `"text"`, `'text'`
- Code: `` `code` ``, ```code blocks```
- URLs: `https://example.com`
- Tables: Markdown tables with `|`
- Lists: Both unordered (`-`, `*`, `+`) and numbered

### 2. Chunk Object

**Structure**:
```python
@dataclass
class Chunk:
    index: int                    # Order in original text
    text: str                     # Main chunk content
    overlap_start: str            # Context from previous chunk
    overlap_end: str              # Context for next chunk
    has_overlap_start: bool       # Whether this chunk has leading context
    has_overlap_end: bool         # Whether this chunk provides context to next
    original_markers: Dict        # Formatting and structure metadata
```

**Markers Tracked**:
- `has_list`: Contains list items
- `has_numbered_list`: Contains numbered list
- `has_heading`: Contains Markdown headings
- `has_blockquote`: Contains block quotes
- `has_code`: Contains code blocks
- `starts_with_list`: Chunk begins with list item
- `paragraph_count`: Number of paragraphs in chunk

### 3. TextRejoiner Class

**Purpose**: Reassemble processed chunks seamlessly.

**Features**:
- Maintains strict order fidelity
- Removes duplicate overlap text
- Validates structural integrity
- Preserves formatting

**Overlap Removal**:
Uses fuzzy sentence matching (70% similarity threshold) to identify and remove overlapping content that was added for context.

**Validation Checks**:
- Quote balance (warnings only)
- Parentheses balance (warnings only)
- Paragraph count consistency (with tolerance)
- Structure marker preservation

## Chunking Logic

### Step 1: Paragraph-Based Splitting

```
Original Text
    │
    ├─ Split on double newlines
    │
    ▼
Paragraph 1 (100 words)
Paragraph 2 (250 words)
Paragraph 3 (180 words)
Paragraph 4 (600 words)  ← Too large!
Paragraph 5 (120 words)
```

### Step 2: Chunk Building

```
Current Chunk: []
Word Count: 0

Add Para 1 (100w) → Chunk: [Para1], Count: 100
Add Para 2 (250w) → Chunk: [Para1, Para2], Count: 350
Add Para 3 (180w) → Would be 530w, EXCEEDS MAX (400w)
    → Finish Chunk 1: [Para1, Para2]
    → Extract overlap (last 2 sentences)
    → Start Chunk 2: [Para3], Count: 180

Para 4 is 600w → TOO LARGE
    → Finish Chunk 2: [Para3]
    → Split Para 4 by sentences
    → Create Chunk 3 from first 400w of Para 4
    → Create Chunk 4 from remaining Para 4

Add Para 5 (120w) → Chunk 5: [Para5], Count: 120
```

### Step 3: Overlap Addition

```
Chunk 1: "...sentence A. Sentence B."
         Extract overlap: "Sentence A. Sentence B."

Chunk 2: "Sentence A. Sentence B.\n\nParagraph 3 text..."
         ↑ Overlap added for context

After processing:
Chunk 1 → Processed 1
Chunk 2 → Processed 2 (still contains overlap at start)
```

### Step 4: Rejoining

```
Processed 1: "...rewritten sentence A. Rewritten sentence B."

Processed 2: "Rewritten sentence A. Rewritten sentence B.
              Rewritten paragraph 3..."

Rejoiner:
1. Keep Processed 1 as-is
2. Find "Rewritten sentence B" in Processed 2
3. Remove everything up to and including it
4. Result: "Rewritten paragraph 3..."
5. Join: Processed 1 + "\n\n" + Cleaned Processed 2
```

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Chunking Configuration
ENABLE_CHUNKING=True              # Enable/disable chunking system
CHUNK_MIN_SIZE=200                # Minimum words per chunk
CHUNK_MAX_SIZE=400                # Maximum words per chunk
CHUNKING_THRESHOLD=500            # Word count before chunking kicks in
```

### When Chunking Activates

```
Word Count ≥ CHUNKING_THRESHOLD → Chunking enabled
Word Count < CHUNKING_THRESHOLD → Direct processing
```

**Example**:
- Input: 800 words
- Threshold: 500 words
- Result: **Chunked** into 2-3 chunks of ~300-400 words each

## Usage Examples

### Example 1: Medium Text (No Chunking)

```python
text = "..." # 450 words
result = humanize_text(text, engine="gemini")
# Processed directly without chunking
```

### Example 2: Large Text (With Chunking)

```python
text = "..." # 1500 words
result = humanize_text(text, engine="openai")

# Behind the scenes:
# 1. TextChunker splits into 4 chunks (300-400 words each)
# 2. Each chunk processed with overlap context
# 3. TextRejoiner seamlessly combines results
# 4. Returns unified, humanized text
```

### Example 3: Manual Chunking Control

```python
from humanizer.chunking import TextChunker, TextRejoiner
from humanizer.utils import humanize_with_gemini

# Custom chunking parameters
chunker = TextChunker(
    min_chunk_size=150,
    max_chunk_size=300,
    overlap_sentences=3  # More overlap for better context
)

# Split text
chunks = chunker.chunk_text(large_text)

# Process each chunk
processed = []
for chunk in chunks:
    chunk_input = f"{chunk.overlap_start}\n\n{chunk.text}" if chunk.has_overlap_start else chunk.text
    result = humanize_with_gemini(chunk_input)
    processed.append((chunk, result))

# Rejoin
rejoiner = TextRejoiner()
final_text = rejoiner.rejoin_chunks(processed)
```

## Edge Cases Handled

### 1. Single Large Paragraph

```
Input: One paragraph with 800 words
Solution: Split by sentences into multiple chunks
```

### 2. Short Text

```
Input: 300 words
Solution: Skip chunking, process directly
```

### 3. Text with Citations

```
Input: "Study shows [Author, 2020] that..."
Protection: Citation kept intact, never split
```

### 4. Code Blocks

```
Input:
```python
def function():
    return value
```
Protection: Entire code block kept in one chunk
```

### 5. Lists

```
Input:
1. First item spanning
   multiple lines
2. Second item

Protection: Each complete list item kept together
```

### 6. Failed Chunk Processing

```
Scenario: Chunk 2 fails due to API error
Solution:
1. Retry chunk 2 once
2. If still fails, raise error with chunk index
3. User can retry the entire operation
```

## Performance Characteristics

### Processing Time

```
Direct Processing (< 500 words):
- Single API call
- Time: ~2-5 seconds

Chunked Processing (1500 words):
- 4 chunks processed sequentially
- Time: ~8-20 seconds (4 × single chunk time)

Future Optimization:
- Parallel chunk processing
- Time: ~2-5 seconds (same as single chunk)
```

### Memory Usage

```
Small Text (< 500 words):
- Minimal: Just input + output

Large Text (2000 words):
- Chunks: ~5-6 chunks in memory
- Overlap: ~50-100 extra words per chunk
- Total: < 3000 words in memory at peak
```

## Quality Assurance

### Validation Steps

1. **Pre-Processing**:
   - Identify protected spans
   - Verify chunk boundaries don't split protected content
   - Confirm all chunks have valid text

2. **Post-Processing**:
   - Verify chunk order preserved
   - Check for duplicate sentences at joins
   - Validate structure markers maintained
   - Confirm total length is reasonable

3. **Structure Checks**:
   - Quote balance (warnings)
   - Parentheses balance (warnings)
   - Paragraph count within tolerance
   - No missing or duplicated content

### Error Handling

```python
try:
    result = humanize_text_with_engine(large_text, "gemini")
except RuntimeError as e:
    # Specific chunk failure: "Failed to process chunk 2: API error"
    # Can retry or inspect chunk 2 specifically
    print(f"Error: {e}")
```

## Testing

### Test Cases

1. **Small text (< threshold)**: Direct processing
2. **Medium text (500-800 words)**: 2-3 chunks
3. **Large text (1500-2000 words)**: 4-6 chunks
4. **Text with citations**: Citations preserved
5. **Text with code blocks**: Code preserved
6. **Text with lists**: Lists preserved
7. **Text with tables**: Tables preserved
8. **Mixed formatting**: All markers preserved

### Expected Outcomes

- ✅ No duplicate sentences at chunk boundaries
- ✅ No missing content
- ✅ Structure and formatting preserved
- ✅ Seamless reading experience
- ✅ Output looks like single-pass humanization

## Troubleshooting

### Issue: Duplicate sentences at joins

**Cause**: Overlap removal failed to find match  
**Solution**: Increase overlap_sentences for more context

### Issue: Missing content

**Cause**: Chunk boundary split protected span  
**Solution**: Check protected span detection patterns

### Issue: Broken formatting

**Cause**: Structure markers not preserved  
**Solution**: Verify original_markers extraction

### Issue: Too many chunks

**Cause**: MAX_CHUNK_SIZE too small  
**Solution**: Increase CHUNK_MAX_SIZE in .env

## Future Enhancements

1. **Parallel Processing**: Process chunks concurrently
2. **Adaptive Chunking**: Adjust chunk size based on content type
3. **Smart Overlap**: Variable overlap based on content complexity
4. **Streaming**: Return chunks as they're processed
5. **Caching**: Cache similar chunks to reduce API calls
6. **Quality Metrics**: Measure join quality with similarity scores

## API Reference

See inline docstrings in:
- `humanizer/chunking.py` - TextChunker, TextRejoiner, Chunk
- `humanizer/utils.py` - humanize_with_chunking()
