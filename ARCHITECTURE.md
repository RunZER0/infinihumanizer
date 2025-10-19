# InfiniHumanizer Architecture Diagram

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Browser @ localhost:8000)                 │
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                    │
│  │   Textarea   │         │  Dropdown    │                     │
│  │  (Input)     │         │  ┌────────┐  │                     │
│  │              │         │  │  OXO   │  │ (Gemini)           │
│  │              │         │  │  smurk │  │ (OpenAI)           │
│  └──────────────┘         └──┴────────┴──┘                     │
│         │                        │                              │
│         │    [Humanize Button]   │                              │
│         └────────────┬───────────┘                              │
└──────────────────────┼──────────────────────────────────────────┘
                       │ HTTP POST
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO BACKEND                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   humanizer/views.py                     │  │
│  │  • Receives POST with text + engine                      │  │
│  │  • Validates input                                       │  │
│  │  • Checks user quota                                     │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   humanizer/utils.py                     │  │
│  │                    (Main Interface)                      │  │
│  │                                                          │  │
│  │  humanize_text_with_engine(text, engine)                │  │
│  │         │                                                │  │
│  │         ├─── if engine == "gemini"  ──────┐             │  │
│  │         └─── if engine == "openai" ────┐  │             │  │
│  └─────────────────────────────────────┼──┼──┼─────────────┘  │
│                                        │  │  │                 │
└────────────────────────────────────────┼──┼──┼─────────────────┘
                                         │  │  │
                    ┌────────────────────┘  │  └────────────────┐
                    ▼                       ▼                    ▼
        ┌───────────────────────┐  ┌───────────────────────┐
        │   llm_engines/        │  │   llm_engines/        │
        │   gemini_engine.py    │  │   openai_engine.py    │
        │                       │  │                       │
        │  class GeminiEngine   │  │  class OpenAIEngine   │
        │  ┌─────────────────┐  │  │  ┌─────────────────┐  │
        │  │ __init__()      │  │  │  │ __init__()      │  │
        │  │ • Load API key  │  │  │  │ • Load API key  │  │
        │  │ • Config model  │  │  │  │ • Create client │  │
        │  └─────────────────┘  │  │  └─────────────────┘  │
        │  ┌─────────────────┐  │  │  ┌─────────────────┐  │
        │  │ humanize(text)  │  │  │  │ humanize(text)  │  │
        │  │ 1. Get prompts  │  │  │  │ 1. Get prompts  │  │
        │  │ 2. Call API     │  │  │  │ 2. Call API     │  │
        │  │ 3. Return result│  │  │  │ 3. Return result│  │
        │  └─────────────────┘  │  │  └─────────────────┘  │
        └───────────┬───────────┘  └───────────┬───────────┘
                    │                          │
                    │   Both import from       │
                    │           ▼              │
                    │  ┌─────────────────┐    │
                    └─▶│  prompts.py     │◀───┘
                       │                 │
                       │ SYSTEM_PROMPT   │ (Shared)
                       │ get_user_prompt()│
                       └─────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
    ┌────────────────────────┐    ┌────────────────────────┐
    │   Google Gemini API    │    │    OpenAI API          │
    │   (OXO)                │    │    (smurk)             │
    │                        │    │                        │
    │ • gemini-2.5-flash     │    │ • gpt-4                │
    │ • System instruction   │    │ • Chat completions     │
    │ • Generate content     │    │ • System + user msg    │
    └────────────┬───────────┘    └────────────┬───────────┘
                 │                             │
                 └──────────┬──────────────────┘
                            ▼
                   Humanized Text Result
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Response to UI    │
                 │   (JSON/HTML)       │
                 └─────────────────────┘
```

## 📊 Data Flow

### Request Flow
```
1. User Input
   ├─ Text: "Your content here..."
   └─ Engine: "gemini" or "openai"
        │
        ▼
2. Django View (humanizer_view)
   ├─ Authenticate user
   ├─ Validate input
   ├─ Check quota
   └─ Call utils.humanize_text_with_engine(text, engine)
        │
        ▼
3. Utils Router
   ├─ Normalize engine name
   ├─ Route to appropriate engine
   └─ if "gemini" → humanize_with_gemini()
      if "openai" → humanize_with_openai()
        │
        ▼
4. Engine Class
   ├─ GeminiEngine() or OpenAIEngine()
   ├─ Load API key from env
   ├─ Initialize client/model
   └─ Call humanize(text)
        │
        ▼
5. Prompt Building
   ├─ Get SYSTEM_PROMPT from prompts.py
   ├─ Get user_prompt = get_user_prompt(text)
   └─ Combine for API call
        │
        ▼
6. API Call
   ├─ Gemini: model.generate_content(user_prompt)
   │          with system_instruction=SYSTEM_PROMPT
   │
   └─ OpenAI: client.chat.completions.create(
                  messages=[
                      {role: "system", content: SYSTEM_PROMPT},
                      {role: "user", content: user_prompt}
                  ])
        │
        ▼
7. Response Processing
   ├─ Extract text from response
   ├─ Clean up newlines
   └─ Return humanized text
        │
        ▼
8. View Response
   ├─ Update user quota
   ├─ Store in session
   └─ Return JSON/HTML to frontend
        │
        ▼
9. UI Update
   └─ Display humanized text in output area
```

## 🗂️ Module Dependencies

```
humanizer/utils.py
    │
    ├─── imports from → llm_engines/__init__.py
    │                       │
    │                       ├─── exports → GeminiEngine
    │                       ├─── exports → OpenAIEngine
    │                       └─── exports → prompts
    │
    └─── calls → GeminiEngine() or OpenAIEngine()
                      │                    │
                      ▼                    ▼
              gemini_engine.py      openai_engine.py
                      │                    │
                      ├─── imports → prompts.py
                      │                    │
                      └────────┬───────────┘
                               │
                               ▼
                        prompts.py
                        ├─ SYSTEM_PROMPT
                        └─ get_user_prompt()
```

## 🔐 Configuration Flow

```
Environment Variables (.env)
    │
    ├─── GEMINI_API_KEY ────────┐
    ├─── GEMINI_MODEL          │
    ├─── OPENAI_API_KEY ────┐  │
    └─── OPENAI_MODEL       │  │
                            │  │
                            ▼  ▼
                    ┌──────────────────┐
                    │ Django Settings  │
                    │ (core/settings.py)│
                    └──────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        GeminiEngine              OpenAIEngine
        │                         │
        ├─ self.api_key          ├─ self.api_key
        └─ self.model_name       └─ self.model_name
```

## 🎯 Error Handling Chain

```
API Error (e.g., invalid key)
    │
    ▼
Engine catches & raises RuntimeError
    │
    ▼
utils.py propagates error up
    │
    ▼
views.py catches error
    │
    ├─── logs error
    ├─── creates user message
    └─── returns error response
         │
         ▼
    Frontend displays error
```

## 📝 File Relationships

```
├─ humanizer/
│  ├─ utils.py (85 lines)
│  │  └─ Simple router, no business logic
│  │
│  ├─ views.py
│  │  └─ Uses utils.humanize_text_with_engine()
│  │
│  └─ llm_engines/
│     ├─ __init__.py (15 lines)
│     │  └─ Exports for easy importing
│     │
│     ├─ prompts.py (65 lines)
│     │  └─ Single source of truth for prompts
│     │
│     ├─ gemini_engine.py (~95 lines)
│     │  ├─ GeminiEngine class
│     │  ├─ Uses prompts.py
│     │  └─ google.generativeai integration
│     │
│     └─ openai_engine.py (~65 lines)
│        ├─ OpenAIEngine class
│        ├─ Uses prompts.py
│        └─ openai SDK integration
```

## 🧩 Component Isolation

Each component has a single, clear responsibility:

```
┌────────────────────────┐
│       prompts.py       │  What to ask AI
│  "Prompt Engineering"  │
└────────────────────────┘

┌────────────────────────┐
│   gemini_engine.py     │  How to talk to Gemini
│   "Gemini Integration" │
└────────────────────────┘

┌────────────────────────┐
│   openai_engine.py     │  How to talk to OpenAI
│   "OpenAI Integration" │
└────────────────────────┘

┌────────────────────────┐
│       utils.py         │  Which engine to use
│    "Router/Gateway"    │
└────────────────────────┘

┌────────────────────────┐
│       views.py         │  Handle web requests
│   "HTTP Interface"     │
└────────────────────────┘
```

## ✅ Why This Structure Works

1. **Separation of Concerns**: Each file does ONE thing
2. **DRY (Don't Repeat Yourself)**: Prompts defined once, used by both
3. **Open/Closed Principle**: Open for extension (add engines), closed for modification
4. **Easy Testing**: Each component can be tested independently
5. **Clear Dependencies**: Linear, no circular imports
6. **Scalable**: Easy to add more engines or features

## 🚀 Adding a New Engine

```
1. Create new file: llm_engines/anthropic_engine.py
2. Define class: AnthropicEngine
3. Implement: humanize(text) method
4. Use: prompts.SYSTEM_PROMPT and get_user_prompt()
5. Export in: llm_engines/__init__.py
6. Add case in: utils.humanize_text_with_engine()
7. Update UI: Add option to dropdown

That's it! No need to modify existing engine code.
```
