# InfiniHumanizer - Clean File Structure

## Overview
The humanizer module has been reorganized for clarity and maintainability. All LLM processing is isolated in a dedicated module with clear separation of concerns.

## New Structure

```
humanizer/
├── utils.py                    # Main interface - simple and clean
├── views.py                    # Django views
├── models.py                   # Database models
├── urls.py                     # URL routing
└── llm_engines/                # ✨ NEW: LLM integrations module
    ├── __init__.py             # Module exports
    ├── README.md               # Module documentation
    ├── prompts.py              # Shared prompts for all engines
    ├── gemini_engine.py        # Google Gemini (OXO) integration
    └── openai_engine.py        # OpenAI (smurk) integration
```

## File Purposes

### `humanizer/utils.py` ⭐ Main Entry Point
**Purpose**: Clean, simple interface for humanizing text  
**Lines**: ~85 lines (down from 150+)  
**Functions**:
- `humanize_text(text, engine=None)` - Main entry point
- `humanize_text_with_engine(text, engine)` - Router function
- `humanize_with_gemini(text)` - Gemini wrapper
- `humanize_with_openai(text)` - OpenAI wrapper

**Key Features**:
- No complex logic - just routing
- Well-documented with docstrings
- Type hints for all functions
- Clean error handling

### `humanizer/llm_engines/` 📦 LLM Module

#### `prompts.py`
**Purpose**: Central location for all AI prompts  
**Contents**:
- `SYSTEM_PROMPT`: Comprehensive human-writing instructions
- `get_user_prompt(text)`: Formats user prompt with text

**Why Separate?**  
- Easy to update prompts without touching engine code
- Both engines use identical prompts for consistency
- Can be tested independently

#### `gemini_engine.py` (OXO)
**Purpose**: Google Gemini API integration  
**Class**: `GeminiEngine`  
**Method**: `humanize(text) -> str`  
**Features**:
- Initialization with API key validation
- Uses `system_instruction` parameter
- Response text extraction with fallbacks
- Clean error messages

#### `openai_engine.py` (smurk)
**Purpose**: OpenAI API integration  
**Class**: `OpenAIEngine`  
**Method**: `humanize(text) -> str`  
**Features**:
- Initialization with API key validation
- Uses chat completions API
- System + user message structure
- Clean error messages

## Benefits of New Structure

### ✅ Clarity
- Each file has ONE clear purpose
- Easy to find where something is
- No mixing of concerns

### ✅ Maintainability
- Update prompts in one place → affects both engines
- Engine-specific code is isolated
- Easy to add new engines (just add new file)

### ✅ Testability
- Each engine can be tested independently
- Prompts can be tested separately
- Utils just tests routing logic

### ✅ Debugging
- Clear error messages show which engine failed
- Stack traces point to specific engine files
- No complex nested logic

### ✅ Documentation
- Each file has module-level docstring
- Every function has detailed docstring
- Type hints show expected inputs/outputs
- README in llm_engines/ explains structure

## Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional (with defaults)
GEMINI_MODEL=gemini-2.5-flash
OPENAI_MODEL=gpt-4
HUMANIZER_ENGINE=gemini
```

### Dependencies (requirements.txt)
```
openai==1.12.0          # ⚠️ Important: Version locked for compatibility
httpx==0.24.1           # ⚠️ Must match openai version
httpcore==0.17.3        # ⚠️ Must match httpx version
google-generativeai==0.8.3
```

## Usage Examples

### Basic Usage
```python
from humanizer.utils import humanize_text

# Use default engine (gemini)
result = humanize_text("Your text here")

# Specify engine
result = humanize_text("Your text", engine="openai")
result = humanize_text("Your text", engine="gemini")
```

### Direct Engine Usage
```python
from humanizer.llm_engines import GeminiEngine, OpenAIEngine

# Use Gemini directly
gemini = GeminiEngine()
result = gemini.humanize("Your text")

# Use OpenAI directly
openai = OpenAIEngine()
result = openai.humanize("Your text")
```

### In Django Views
```python
from humanizer.utils import humanize_text_with_engine

def my_view(request):
    text = request.POST.get('text')
    engine = request.POST.get('engine', 'gemini')
    
    try:
        result = humanize_text_with_engine(text, engine)
        return JsonResponse({'result': result})
    except RuntimeError as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Error Handling

### Missing API Keys
```python
RuntimeError: GEMINI_API_KEY not set in environment
RuntimeError: OPENAI_API_KEY not set in environment
```

### Empty Responses
```python
RuntimeError: Empty response from Gemini API
RuntimeError: Empty response from OpenAI API
```

### Invalid Engine
```python
ValueError: Unknown engine: xyz. Use 'gemini' or 'openai'
```

## Future Enhancements

### Easy to Add
1. **New engines**: Just add `new_engine.py` in `llm_engines/`
2. **Engine-specific prompts**: Add to engine class
3. **Streaming responses**: Add `humanize_streaming()` method
4. **Caching**: Add caching layer in utils.py
5. **Rate limiting**: Add to individual engines

### Architecture Supports
- A/B testing different prompts
- Multi-model ensembles
- Fallback chains (try OpenAI, fallback to Gemini)
- Cost tracking per engine
- Performance monitoring

## Migration Notes

### What Changed
- ❌ Removed: All local/offline processing logic
- ❌ Removed: Complex prompt building in utils.py
- ✅ Added: Dedicated `llm_engines/` module
- ✅ Added: Clean class-based engine interface
- ✅ Added: Shared prompts system
- ✅ Fixed: OpenAI SDK version compatibility

### Breaking Changes
- None! All public functions (`humanize_text`, `humanize_text_with_engine`) work the same

### Backward Compatibility
```python
# All these still work exactly as before
from humanizer.utils import humanize_text
from humanizer.utils import humanize_text_with_engine  
from humanizer.utils import humanize_with_gemini
from humanizer.utils import humanize_with_openai
```

## Troubleshooting

### Server won't start
1. Check `requirements.txt` versions match
2. Reinstall: `pip install -r requirements.txt`
3. Check for syntax errors in new files

### OpenAI "proxies" error
- **Cause**: Wrong openai/httpx version combination
- **Fix**: `pip install openai==1.12.0 httpx==0.24.1`

### Import errors
- **Cause**: Missing `__init__.py` or empty files
- **Fix**: Check all `llm_engines/` files exist and have content

### Engine not working
1. Check API key is set: `echo $env:GEMINI_API_KEY`
2. Check error logs for specific API errors
3. Test engine directly in Python shell

## Testing Checklist

- [ ] Server starts without errors
- [ ] Can login with admin@example.com / admin1234
- [ ] OXO (Gemini) engine works
- [ ] smurk (OpenAI) engine works
- [ ] Both produce different outputs
- [ ] Error messages are clear
- [ ] UI dropdown shows OXO and smurk
- [ ] Results display properly

## Server Commands

```powershell
# Stop server on port 8000
$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if ($conn) { $pids = $conn | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique; foreach ($pid in $pids) { try { Stop-Process -Id $pid -Force } catch {} } }

# Start server
C:/Users/USER/Documents/infinihumanizer/venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000

# Test imports
C:/Users/USER/Documents/infinihumanizer/venv/Scripts/python.exe -c "from humanizer.utils import humanize_text; print('OK')"
```

## Summary

The new structure is:
- **Cleaner**: Each file has one clear purpose
- **Simpler**: Less code, more documentation
- **Maintainable**: Easy to update and extend
- **Reliable**: Fixed version compatibility issues
- **Professional**: Follows Python best practices

All humanization now strictly goes through the LLM APIs with your custom prompts. No local processing, no fallbacks, just clean API calls.
