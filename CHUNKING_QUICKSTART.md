# Chunking System Quick Start

## 🎯 What It Does

Automatically splits large texts (500+ words) into manageable chunks (200-400 words), processes each chunk through the LLM, and seamlessly rejoins them **without any post-processing**.

## ⚡ Quick Facts

- **Automatic**: Kicks in for texts ≥ 500 words
- **Intelligent**: Respects sentences, paragraphs, citations, code, lists
- **Seamless**: No visible joins or duplicates in output
- **Fast**: Processes chunks sequentially (future: parallel)
- **Safe**: Preserves all formatting and structure

## 🔧 Configuration (.env)

```bash
ENABLE_CHUNKING=True          # Turn chunking on/off
CHUNK_MIN_SIZE=200            # Minimum words per chunk
CHUNK_MAX_SIZE=400            # Maximum words per chunk  
CHUNKING_THRESHOLD=500        # Words before chunking starts
```

## 📊 How It Works

### Small Text (< 500 words)
```
Input (400 words) → Direct Processing → Output
```

### Large Text (≥ 500 words)
```
Input (1500 words)
    ↓
Split into chunks (with overlap)
    ↓
Chunk 1 (350w) → Process → Result 1
Chunk 2 (370w) → Process → Result 2  
Chunk 3 (380w) → Process → Result 3
Chunk 4 (350w) → Process → Result 4
    ↓
Remove overlaps & rejoin
    ↓
Final Output (seamless)
```

## 🛡️ What's Protected

The chunker **never splits** these:

- ✅ Citations: `[Author, 2020]`
- ✅ Quotes: `"quoted text"`
- ✅ Code: `` `code` `` or ```code blocks```
- ✅ URLs: `https://example.com`
- ✅ Tables: Markdown tables
- ✅ List items: Complete bullet or numbered items

## 🎓 Examples

### Example 1: Academic Paper (1200 words)

**Input**:
```
Abstract (200w)

Introduction (400w)

Methods (300w)

Results (300w)
```

**Chunking**:
```
Chunk 1: Abstract + Introduction (600w total)
         But with overlap: ~350w in chunk
         
Chunk 2: Introduction (last 2 sentences) + Methods (320w)

Chunk 3: Methods (last 2 sentences) + Results (320w)
```

**Output**: Single seamless paper with natural flow

### Example 2: Blog Post with Code (800 words)

**Input**:
```
Introduction (200w)

Code Example:
```python
def example():
    return "code"
```

Explanation (400w)
```

**Chunking**:
```
Chunk 1: Introduction + Code block (stays together!)

Chunk 2: Code block (last 2 lines as overlap) + Explanation
```

**Output**: Code preserved perfectly, no splits

## 🧪 Testing Chunking

### Test 1: Verify Chunking Threshold

```python
# Small text - should NOT chunk
short_text = " ".join(["word"] * 400)
result = humanize_text(short_text)
# Logs show: Direct processing (no chunking)

# Large text - SHOULD chunk
long_text = " ".join(["word"] * 1000)
result = humanize_text(long_text)
# Logs show: Chunking activated, N chunks processed
```

### Test 2: Verify No Duplicates

```python
long_text = """
Paragraph 1 with multiple sentences. This is another sentence.

Paragraph 2 with more content. And yet another sentence.

Paragraph 3 continues the theme.
""" * 20  # Make it large

result = humanize_text(long_text)

# Check: No sentence appears twice
sentences = result.split('. ')
assert len(sentences) == len(set(sentences))
```

### Test 3: Verify Structure Preservation

```python
text_with_list = """
Introduction paragraph.

Key points:
1. First point
2. Second point
3. Third point

Conclusion paragraph.
""" * 10  # Make it large

result = humanize_text(text_with_list)

# Check: All list items present
assert "1." in result
assert "2." in result
assert "3." in result
```

## 📈 Performance

| Text Size | Chunks | Processing Time | Memory |
|-----------|--------|-----------------|--------|
| < 500w    | 0      | ~2-5s           | Low    |
| 500-800w  | 2      | ~4-10s          | Low    |
| 800-1200w | 3      | ~6-15s          | Medium |
| 1200-2000w| 4-5    | ~8-25s          | Medium |

## 🐛 Troubleshooting

### Issue: "Duplicate sentences at joins"

**Fix**: Increase overlap for better matching
```bash
# In code (custom usage)
chunker = TextChunker(overlap_sentences=3)  # Default is 2
```

### Issue: "Chunking not activating"

**Check**:
1. Word count ≥ `CHUNKING_THRESHOLD` (500)?
2. `ENABLE_CHUNKING=True` in .env?
3. Server restarted after .env changes?

### Issue: "Missing content after rejoining"

**Cause**: Protected span was split  
**Fix**: Check `_identify_protected_spans()` patterns

### Issue: "Broken formatting"

**Cause**: Structure markers not preserved  
**Fix**: Verify `original_markers` extraction

## 💡 Tips

1. **Optimize for your content**: Adjust `CHUNK_MAX_SIZE` based on typical paragraph length
2. **More overlap = better context**: Increase `overlap_sentences` for complex texts
3. **Monitor logs**: Check for "Chunking activated" messages
4. **Test incrementally**: Start with small increases in text size
5. **Preserve structure**: Use proper Markdown for best results

## 🔍 Monitoring

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# You'll see:
# DEBUG: Chunking activated: 1234 words, threshold 500
# DEBUG: Created 3 chunks
# DEBUG: Processing chunk 1/3
# DEBUG: Processing chunk 2/3
# DEBUG: Processing chunk 3/3
# DEBUG: Rejoining 3 chunks
# DEBUG: Final text: 1234 words
```

### Check Chunk Boundaries

```python
from humanizer.chunking import TextChunker

chunker = TextChunker()
chunks = chunker.chunk_text(your_large_text)

for i, chunk in enumerate(chunks):
    print(f"\n=== Chunk {i+1}/{len(chunks)} ===")
    print(f"Words: {len(chunk.text.split())}")
    print(f"Has overlap start: {chunk.has_overlap_start}")
    print(f"Has overlap end: {chunk.has_overlap_end}")
    print(f"First 100 chars: {chunk.text[:100]}...")
    print(f"Last 100 chars: ...{chunk.text[-100:]}")
```

## 🚀 Next Steps

1. **Try it**: Submit a 1000+ word text through the UI
2. **Monitor**: Check server logs for chunking activity
3. **Compare**: Process same text with chunking on/off
4. **Optimize**: Tune chunk sizes for your use case
5. **Extend**: Add custom protected span patterns

## 📚 Full Documentation

- `CHUNKING_SYSTEM.md` - Complete technical docs
- `humanizer/chunking.py` - Source code with docstrings
- `ARCHITECTURE.md` - System architecture diagrams

## ✅ Checklist

- [ ] `.env` has chunking configuration
- [ ] Server restarted after .env changes
- [ ] Tested with < 500 words (should NOT chunk)
- [ ] Tested with > 500 words (SHOULD chunk)
- [ ] Verified no duplicate sentences
- [ ] Verified structure preserved
- [ ] Checked both OXO and smurk engines
- [ ] Reviewed logs for errors

---

**Ready to test?** Visit http://127.0.0.1:8000/humanizer/ and paste a large text!
