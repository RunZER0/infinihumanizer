# 🎯 HUMANIZATION LOGIC - COMPLETE GUIDE

## Where to Edit Everything

All the humanization logic is centralized and easy to edit. Here's exactly where to find each component:

---

## 📋 MAIN CONFIGURATION FILE (EDIT THIS!)

### **`humanizer/engine_config.py`** ⭐ PRIMARY EDIT LOCATION

**This is your main control center!** Edit this file to customize:
- System prompts for each model
- Temperature settings
- Error injection rules
- Vocabulary guidance
- All model behavior

#### File Location:
```
infinihumanizer/humanizer/engine_config.py
```

#### What's Inside:

```python
# ============================================================================
# DEEPSEEK ENGINE (Loly) - Balanced Model
# ============================================================================

DEEPSEEK_CONFIG = {
    "name": "DeepSeek (Loly)",
    "model": "deepseek-chat",
    
    # ⚙️ EDIT THESE TEMPERATURE SETTINGS:
    "base_temperature": 0.7,           # 0.0 = focused, 1.0 = creative
    "temperature_variation": 0.15,     # How much to vary per chunk
    "max_tokens": 4000,
    
    # 📝 EDIT THIS SYSTEM PROMPT:
    "system_prompt": """YOUR CUSTOM INSTRUCTIONS HERE...""",
    
    # 💬 EDIT THIS USER PROMPT:
    "user_prompt_template": "Humanize this text...\n\n{text}"
}

# ============================================================================
# OPENAI ENGINE (Smurk) - Professional Model
# ============================================================================

OPENAI_CONFIG = {
    "name": "OpenAI (Smurk)",
    "model": "gpt-4",
    
    # ⚙️ EDIT THESE SETTINGS:
    "base_temperature": 0.6,
    "temperature_variation": 0.12,
    "max_tokens": 2000,
    "top_p": 0.9,                      # OpenAI-specific
    "frequency_penalty": 0.2,          # OpenAI-specific
    "presence_penalty": 0.2,           # OpenAI-specific
    
    # 📝 EDIT THIS SYSTEM PROMPT:
    "system_prompt": """YOUR CUSTOM INSTRUCTIONS HERE...""",
    
    # 💬 EDIT THIS USER PROMPT:
    "user_prompt_template": "Humanize this text...\n\n{text}"
}
```

---

## 🔧 WHAT YOU CAN CUSTOMIZE

### 1. **System Prompts** (Main Instructions)

**Location:** `engine_config.py` → `DEEPSEEK_CONFIG["system_prompt"]` or `OPENAI_CONFIG["system_prompt"]`

**What it does:** Main instructions that tell the AI how to humanize text

**Current length:** 
- DeepSeek: ~70 lines
- OpenAI: ~85 lines

**How to edit:**
```python
"system_prompt": """
Put your custom instructions here.
You can write multiple lines.
The AI will follow these instructions for every humanization.
"""
```

**Examples of what to change:**
- Error injection rate (currently 12-18%)
- Vocabulary sophistication level
- Tone (formal vs casual)
- Specific error types to inject
- Preservation rules

---

### 2. **Temperature Settings** (Creativity Level)

**Location:** `engine_config.py` → `"base_temperature"` and `"temperature_variation"`

**What it does:** Controls how creative/random the AI output is

**Current values:**
- **DeepSeek:** base=0.7, variation=0.15
- **OpenAI:** base=0.6, variation=0.12

**Temperature scale:**
- `0.0` = Focused, deterministic, consistent
- `0.5` = Balanced
- `1.0` = Creative, random, diverse

**How to edit:**
```python
"base_temperature": 0.8,        # Make it more creative
"temperature_variation": 0.2,   # Vary more between chunks
```

**Temperature variation:** Each chunk gets a slightly different temperature to add natural variation
- Chunk 0: base_temp
- Chunk 1: base_temp + (variation/4)
- Chunk 2: base_temp + (variation/2)
- Chunk 3: base_temp + (3*variation/4)
- Then repeats

---

### 3. **User Prompt Template**

**Location:** `engine_config.py` → `"user_prompt_template"`

**What it does:** The message sent to the AI with each text chunk

**Current value:**
```python
"user_prompt_template": "Humanize this text...\n\n{text}"
```

**How to edit:**
```python
"user_prompt_template": "Transform this AI text into human writing:\n\n{text}\n\nRemember: inject errors!"
```

**Note:** `{text}` is automatically replaced with the actual content

---

### 4. **Model Selection**

**Location:** `engine_config.py` → `"model"`

**Current models:**
- DeepSeek: `"deepseek-chat"`
- OpenAI: `"gpt-4"`

**How to change:**
```python
"model": "gpt-4-turbo"          # Use different OpenAI model
"model": "deepseek-reasoner"    # Use different DeepSeek model
```

---

### 5. **OpenAI-Specific Settings**

**Location:** `engine_config.py` → `OPENAI_CONFIG`

**Additional parameters:**
```python
"top_p": 0.9,                   # Nucleus sampling (0.0-1.0)
"frequency_penalty": 0.2,       # Reduce repetition (0.0-2.0)
"presence_penalty": 0.2,        # Encourage new topics (0.0-2.0)
```

**What they do:**
- **top_p:** Controls diversity (lower = more focused)
- **frequency_penalty:** Penalizes repeated tokens
- **presence_penalty:** Encourages new topics/words

---

## 🔍 ENGINE IMPLEMENTATION FILES

### **`humanizer/llm_engines/deepseek_engine.py`**

**What it does:** Handles API calls to DeepSeek

**Key code:**
```python
def humanize(self, text: str, chunk_index: int = 0) -> str:
    # Load config from engine_config.py
    self.config = get_engine_config("deepseek")
    
    # Calculate dynamic temperature
    temperature = calculate_temperature(
        self.config["base_temperature"],
        self.config["temperature_variation"],
        chunk_index
    )
    
    # Get prompts from config
    system_prompt = self.config["system_prompt"]
    user_prompt = self.config["user_prompt_template"].format(text=text)
    
    # Make API call...
```

**Do you need to edit this?** ❌ NO - Only edit if changing API endpoints or error handling

---

### **`humanizer/llm_engines/openai_engine.py`**

**What it does:** Handles API calls to OpenAI

**Key code:**
```python
def humanize(self, text: str, chunk_index: int = 0) -> str:
    # Load config from engine_config.py
    self.config = get_engine_config("openai")
    
    # Calculate dynamic temperature
    temperature = calculate_temperature(...)
    
    # Get prompts from config
    system_prompt = self.config["system_prompt"]
    user_prompt = self.config["user_prompt_template"].format(text=text)
    
    # Make API call with OpenAI SDK...
```

**Do you need to edit this?** ❌ NO - Only edit if changing API behavior

---

## 📊 MAIN ORCHESTRATION

### **`humanizer/views.py`**

**What it does:** Main Django view that handles humanization requests

**Key logic:**
```python
def humanize_view(request):
    # Get user input
    input_text = request.POST.get('text', '')
    selected_engine = request.POST.get('engine', 'deepseek')
    
    # STAGE 1: Preprocessing (analyze text)
    preprocessor = TextPreprocessor()
    analysis = preprocessor.preprocess_text(input_text)
    
    # STAGE 2: Humanization (send to AI engine)
    output_text = humanize_text_with_engine(
        input_text, 
        selected_engine
    )
    
    # STAGE 3: Validation (check quality)
    validator = HumanizationValidator()
    validation_report = validator.validate_humanization(...)
    
    # Return humanized text
    return JsonResponse({'output_text': final_text})
```

**Do you need to edit this?** ❌ NO - Only edit if changing workflow stages

---

### **`humanizer/utils.py`**

**What it does:** Utility function that routes to correct engine

**Key code:**
```python
def humanize_text_with_engine(text: str, engine_name: str) -> str:
    if engine_name == "deepseek":
        engine = DeepSeekEngine()
    elif engine_name == "openai":
        engine = OpenAIEngine()
    
    return engine.humanize(text)
```

**Do you need to edit this?** ❌ NO - Only edit if adding new engines

---

## 🎨 CURRENT PROMPTS SUMMARY

### DeepSeek (Loly) Prompt Focus:
- **12-18% error injection rate**
- **Extremely high perplexity vocabulary**
- **Formal-but-flawed tone**
- **Specific error types:** comma splices, fragments, run-ons, subject-verb disagreement
- **Vocabulary examples:** elucidate, cogitate, paradigmatic, instantiate
- **Temperature:** 0.7 base, ±0.15 variation

### OpenAI (Smurk) Prompt Focus:
- **12-18% error injection rate**
- **Extreme perplexity vocabulary**
- **Semi-academic register**
- **Specific error types:** comma splices, fragments, faulty parallelism, unclear pronouns
- **Vocabulary examples:** evince, manifest, adumbrate, conundrum, exigency
- **Temperature:** 0.6 base, ±0.12 variation

---

## 🚀 QUICK EDIT GUIDE

### Want to change error rate?
**Edit:** `engine_config.py`  
**Find:** `"12-18% ERROR RATE"`  
**Change to:** `"20-25% ERROR RATE"` (or whatever you want)

### Want to make output more creative?
**Edit:** `engine_config.py`  
**Find:** `"base_temperature": 0.7`  
**Change to:** `"base_temperature": 0.9`

### Want to make output more focused/consistent?
**Edit:** `engine_config.py`  
**Find:** `"base_temperature": 0.7`  
**Change to:** `"base_temperature": 0.4`

### Want to change vocabulary level?
**Edit:** `engine_config.py`  
**Find:** The vocabulary section in system_prompt  
**Change:** Add/remove word examples, change sophistication level

### Want to make tone more casual?
**Edit:** `engine_config.py`  
**Find:** `"FORMAL BUT FLAWED TONE"`  
**Change:** Add more casual instructions, reduce academic language

### Want to disable specific error types?
**Edit:** `engine_config.py`  
**Find:** The error type you want to remove (e.g., "COMMA SPLICES")  
**Delete or comment out:** That section

---

## 📝 EXAMPLE CUSTOMIZATION

Let's say you want DeepSeek to be more casual and creative:

**Before:**
```python
DEEPSEEK_CONFIG = {
    "base_temperature": 0.7,
    "system_prompt": """MAINTAIN SEMI-ACADEMIC REGISTER: Sound educated..."""
}
```

**After:**
```python
DEEPSEEK_CONFIG = {
    "base_temperature": 0.85,  # More creative
    "system_prompt": """MAINTAIN CASUAL BUT INTELLIGENT TONE: Sound smart but relaxed.
    
Use contractions (don't, can't, won't).
Use everyday language with occasional sophisticated words.
Keep sentences shorter and punchier.
Be conversational, like you're explaining to a friend.
    
Error injection rate: 15-20% (increased for more human feel)
"""
}
```

---

## 🔄 TESTING YOUR CHANGES

After editing `engine_config.py`:

1. **No server restart needed!** Changes take effect immediately
2. Just refresh the humanizer page
3. Try humanizing text with both engines
4. Check if output matches your new settings

---

## 📂 FILE STRUCTURE OVERVIEW

```
infinihumanizer/
└── humanizer/
    ├── engine_config.py          ⭐ EDIT THIS - All prompts and settings
    ├── views.py                  ℹ️ Main workflow orchestration
    ├── utils.py                  ℹ️ Engine routing
    ├── preprocessing.py          ℹ️ Stage 1: Text analysis
    ├── validation.py             ℹ️ Stage 3: Quality checking
    └── llm_engines/
        ├── deepseek_engine.py    ℹ️ DeepSeek API calls
        └── openai_engine.py      ℹ️ OpenAI API calls
```

**Legend:**
- ⭐ = Primary edit location
- ℹ️ = Reference only (don't usually need to edit)

---

## 🎯 QUICK REFERENCE

| What You Want to Change | File to Edit | What to Look For |
|------------------------|--------------|------------------|
| Error injection rules | `engine_config.py` | `"GRAMMATICAL IMPERFECTIONS"` section |
| Vocabulary sophistication | `engine_config.py` | `"PERPLEXITY VOCABULARY"` section |
| Creativity/randomness | `engine_config.py` | `"base_temperature"` value |
| Model tone (formal/casual) | `engine_config.py` | `"TONE"` sections in system_prompt |
| Output length | `engine_config.py` | `"max_tokens"` value |
| Specific word choices | `engine_config.py` | Vocabulary examples in prompts |
| Error types | `engine_config.py` | Individual error type sections |
| OpenAI penalties | `engine_config.py` | `"frequency_penalty"`, `"presence_penalty"` |

---

## 💡 PRO TIPS

1. **Start small:** Change one thing at a time and test
2. **Keep backups:** Copy `engine_config.py` before major changes
3. **Test both engines:** Make sure changes work for both
4. **Check readability:** Don't make errors so severe that text is unreadable
5. **Temperature sweet spot:** 0.6-0.8 usually gives best results
6. **Error rate balance:** 12-18% is enough to fool detectors without breaking readability

---

## 🆘 TROUBLESHOOTING

**Q: I changed the prompt but output didn't change**  
A: Make sure you saved `engine_config.py`. No restart needed, but file must be saved.

**Q: Output is too random/incoherent**  
A: Lower the `base_temperature` value (try 0.5-0.6)

**Q: Output is too consistent/boring**  
A: Raise the `base_temperature` value (try 0.8-0.9)

**Q: Too many errors, text is unreadable**  
A: Reduce error rate in system prompt (try 8-12% instead of 12-18%)

**Q: Not enough errors, text looks AI-generated**  
A: Increase error rate in system prompt (try 18-25%)

**Q: Want to add a third engine**  
A: Create new config in `engine_config.py`, add engine file in `llm_engines/`, update `utils.py`

---

## 📚 RELATED FILES

- **`prompts.py`** - Old prompt system (DEPRECATED, not used anymore)
- **`nuclear_mode.py`** - Nuclear mode (REMOVED per your request)
- **`chunking.py`** - Text chunking logic (automatic, no editing needed)

---

## ✅ SUMMARY

**To customize humanization behavior:**

1. Open `humanizer/engine_config.py`
2. Find the section for DeepSeek or OpenAI
3. Edit the `system_prompt` (main instructions)
4. Adjust `base_temperature` (creativity level)
5. Modify other settings as needed
6. Save the file
7. Test your changes (no restart needed!)

**That's it!** Everything is centralized in one easy-to-edit file. 🎉
