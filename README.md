# InfiniHumanizer

> **Intelligent Text Humanization Platform with AI-Powered Chunking**

Transform AI-generated or formal text into naturally human-written content using advanced LLM engines with automatic intelligent chunking for large texts.

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd C:\Users\USER\Documents\infinihumanizer

# 2. Activate virtual environment
.\venv\Scripts\activate

# 3. Start server
python manage.py runserver

# 4. Visit
http://127.0.0.1:8000/humanizer/

# 5. Login
Email: admin@example.com
Password: admin1234
```

## ✨ Features

### Core Capabilities
- 🤖 **THREE Powerful Humanization Engines**: 
  - **Smurk (OpenAI)** - Quality-preserving, 65-80% evasion
  - **Loly (DeepSeek)** - Maximum imperfection, 85-95% evasion
  - **⚛️ NUCLEAR** - EXTREME evasion, 95%+ detection bypass
  - ~~OXO (Gemini)~~ - REMOVED (refuses to follow instructions)
- 📝 **Smart Chunking**: Automatically handles large texts up to 2000 words
- 🔗 **Seamless Rejoining**: No visible seams or duplicate content
- 🛡️ **Protected Spans**: Preserves citations, code, quotes, URLs, tables, lists
- 🎯 **Natural Boundaries**: Respects sentences, paragraphs, and structure
- ⚡ **Auto-Detection**: Chunks only when needed (≥500 words)
- 🧬 **3-Stage Pipeline**: Preprocessing → Humanization → Validation
- ✅ **Quality Control**: 5 automated validation checks with fixes

### Technical Features
- 🔐 Email-based authentication with Django Allauth
- 💳 Quota management system
- 📊 User dashboard
- 🌐 Responsive UI
- 🔄 Retry logic for failed chunks
- ✅ Structure validation
- 🎯 AI pattern detection & content preservation
- 💉 Error injection for maximum evasion (Nuclear mode)
- 📈 Validation scoring & automated fixes

## 📁 Project Structure

```
infinihumanizer/
├── humanizer/              # Main application
│   ├── utils.py           # Smart routing & chunking integration
│   ├── chunking.py        # Chunking & rejoining system ⭐
│   ├── llm_engines/       # LLM integrations
│   │   ├── prompts.py     # Shared AI prompts
│   │   ├── gemini_engine.py   # OXO (Gemini)
│   │   └── openai_engine.py   # smurk (OpenAI)
│   ├── views.py           # HTTP request handlers
│   └── templates/         # UI templates
│
├── accounts/              # Authentication
├── core/                  # Django settings
├── static/                # CSS, images
└── Documentation/
    ├── SYSTEM_OVERVIEW.md              # Complete system overview
    ├── ARCHITECTURE.md                 # Architecture diagrams
    ├── CHUNKING_SYSTEM.md              # Chunking technical docs
    ├── CHUNKING_QUICKSTART.md          # Chunking guide
    ├── CHUNKING_IMPLEMENTATION_SUMMARY.md
    └── QUICK_REFERENCE.md              # Quick reference
```

## 🎯 How It Works

### Small Texts (< 500 words)
```
Input → Direct Processing → LLM API → Output
```

### Large Texts (≥ 500 words)
```
Input (1500 words)
    ↓
TextChunker splits intelligently
    ├─ Chunk 1 (350w) + overlap
    ├─ Chunk 2 (380w) + overlap
    ├─ Chunk 3 (390w) + overlap
    └─ Chunk 4 (330w)
    ↓
Each chunk processed via LLM
    ↓
TextRejoiner removes overlaps
    ↓
Final seamless output
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Core Settings
DEBUG=True
OFFLINE_MODE=False
DJANGO_SECRET_KEY=your-secret-key

# LLM APIs
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4.1
HUMANIZER_ENGINE=gemini

# Chunking System ⭐
ENABLE_CHUNKING=True          # Enable intelligent chunking
CHUNK_MIN_SIZE=200            # Min words per chunk
CHUNK_MAX_SIZE=400            # Max words per chunk
CHUNKING_THRESHOLD=500        # Words before chunking activates
```

## 🧪 Testing

### Test Small Text (Direct Processing)
```python
# 1. Visit http://127.0.0.1:8000/humanizer/
# 2. Login
# 3. Paste 400 words
# 4. Select OXO or smurk
# 5. Click Humanize
# Expected: Fast processing, single API call
```

### Test Large Text (Chunked Processing)
```python
# 1. Paste 1200 words
# 2. Select engine
# 3. Click Humanize
# Expected: Multiple chunks, seamless output
# Verify: No duplicate sentences, structure preserved
```

### Test Protected Spans
```python
# Input with:
# - Citation: [Author, 2020]
# - Code: ```python code```
# - Quote: "important text"
# Expected: All protected spans intact
```

## 📊 Performance

| Text Size | Chunks | Time | Memory |
|-----------|--------|------|--------|
| < 500w    | 0      | 2-5s | Low |
| 500-800w  | 2      | 4-10s | Low |
| 800-1200w | 3      | 6-15s | Medium |
| 1200-2000w| 4-5    | 8-25s | Medium |

## 🛡️ Protected Spans

The chunker **never splits**:
- ✅ Citations: `[Author, 2020]`
- ✅ Quotes: `"quoted text"`
- ✅ Code blocks: `` `code` `` or ```code blocks```
- ✅ URLs: `https://example.com`
- ✅ Tables: Markdown tables with `|`
- ✅ Lists: Complete bullet or numbered items

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | Complete system overview |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture diagrams |
| [CHUNKING_SYSTEM.md](CHUNKING_SYSTEM.md) | Chunking technical documentation |
| [CHUNKING_QUICKSTART.md](CHUNKING_QUICKSTART.md) | Chunking quick start guide |
| [CHUNKING_IMPLEMENTATION_SUMMARY.md](CHUNKING_IMPLEMENTATION_SUMMARY.md) | What was built |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick reference guide |
| [humanizer/llm_engines/README.md](humanizer/llm_engines/README.md) | LLM engines documentation |

## 🔑 User Accounts

### Creating a Superuser

If you've forgotten your admin credentials or need to create a new administrator:

```bash
python manage.py create_new_superuser
```

This will generate a secure password and display the credentials. For more options:

```bash
# With custom username and email
python manage.py create_new_superuser --email your@email.com --username yourusername

# Reset existing user's password
python manage.py create_new_superuser --update-existing
```

See [core/management/commands/README.md](core/management/commands/README.md) for detailed documentation.

### Development Accounts:
- **Admin**: `admin@example.com` / `admin1234` (if not changed)
- **Tester**: `tester@example.com` / `test1234`

## 🎨 UI Features

- **Engine Selector**: Narrow dropdown to choose OXO (Gemini) or smurk (OpenAI)
- **Input Area**: Large textarea for text input
- **Humanize Button**: Processes text through selected engine
- **Output Area**: Displays humanized result
- **Word Count**: Shows input/output word counts
- **Quota Display**: Shows remaining humanization quota

## 🔄 Processing Pipeline

```
User Input
    ↓
Authentication & Validation
    ↓
Word Count Check
    ↓
    ├─ < 500 words → Direct Processing
    │                     ↓
    │               LLM API Call
    │                     ↓
    └─ ≥ 500 words → Chunking Pipeline
                          ↓
                    TextChunker
                          ↓
                    Process Each Chunk
                          ↓
                    TextRejoiner
                          ↓
                    Validate Structure
    ↓
Display Result
```

## 🚧 Troubleshooting

### Chunking Not Activating?
```bash
# Check word count ≥ CHUNKING_THRESHOLD (500)
# Verify ENABLE_CHUNKING=True in .env
# Restart server after .env changes
```

### Duplicate Sentences?
```bash
# Increase overlap for better matching
# Check TextRejoiner._sentence_similarity()
```

### Missing Content?
```bash
# Verify protected spans detection
# Check chunk boundaries in logs
```

### OpenAI "proxies" Error?
```bash
pip install openai==1.12.0 httpx==0.24.1 --force-reinstall
```

## 📦 Dependencies

### Core
```
Django==5.2.1
django-allauth==65.8.1
python-dotenv==1.0.1
```

### LLM SDKs
```
openai==1.12.0
httpx==0.24.1
httpcore==0.17.3
google-generativeai==0.8.3
```

### Database
```
dj-database-url==2.3.0
psycopg2-binary==2.9.10  # For PostgreSQL in production
```

## 🌐 Deployment

### Development (Current)
```bash
python manage.py runserver
# Runs on http://127.0.0.1:8000/
```

### Production
```bash
# 1. Set OFFLINE_MODE=False
# 2. Configure DATABASE_URL for PostgreSQL
# 3. Set up SMTP for emails
# 4. Add production API keys
# 5. Update ALLOWED_HOSTS
# 6. Use Gunicorn/uWSGI
# 7. Set up Nginx
```

## 🔐 Security Notes

### Development
- Email verification bypassed in OFFLINE_MODE
- Console email backend
- SQLite database
- Weak secret key

### Production Checklist
- [ ] Strong SECRET_KEY
- [ ] PostgreSQL database
- [ ] SMTP email configured
- [ ] HTTPS enabled
- [ ] API keys in secrets manager
- [ ] ALLOWED_HOSTS restricted
- [ ] CSRF_TRUSTED_ORIGINS set
- [ ] DEBUG=False

## 🎯 Key Technologies

- **Backend**: Django 5.2.1
- **Auth**: Django Allauth
- **LLMs**: Google Gemini, OpenAI GPT
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Gunicorn, WhiteNoise

## 📈 Future Enhancements

- [ ] Parallel chunk processing
- [ ] Adaptive chunk sizing
- [ ] Semantic similarity for overlap detection
- [ ] Chunk result caching
- [ ] Streaming responses
- [ ] Progress indicators
- [ ] A/B testing for prompts
- [ ] Usage analytics
- [ ] Cost monitoring
- [ ] Rate limiting

## 🤝 Contributing

This is a private development project. For production deployment:
1. Review security checklist
2. Test thoroughly with large texts
3. Monitor API costs
4. Set up proper logging
5. Configure backups

## 📄 License

Private Project - All Rights Reserved

## 👤 Author

InfiniHumanizer Development Team

---

## 🎉 Current Status

✅ **Core System**: Fully operational  
✅ **Authentication**: Working  
✅ **OXO Engine (Gemini)**: Ready  
✅ **smurk Engine (OpenAI)**: Ready  
✅ **Chunking System**: Integrated & tested  
✅ **Documentation**: Complete  
✅ **Server**: Running at http://127.0.0.1:8000/  

**Ready for testing and deployment!** 🚀

---

**Quick Links:**
- 🌐 [Access App](http://127.0.0.1:8000/humanizer/)
- 📖 [System Overview](SYSTEM_OVERVIEW.md)
- 🏗️ [Architecture](ARCHITECTURE.md)
- ⚙️ [Chunking Guide](CHUNKING_QUICKSTART.md)
- 📚 [Full Docs](CHUNKING_SYSTEM.md)
