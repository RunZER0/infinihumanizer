# Quick Reference - Infini Humanizer

## 🚀 Start Server
```powershell
cd C:\Users\USER\Documents\infinihumanizer
.\venv\Scripts\activate
python manage.py runserver 127.0.0.1:8000
```

## 🔐 Login Credentials
- **Admin**: `admin@example.com` / `admin1234`
- **Tester**: `tester@example.com` / `test1234`

## 🎯 Engines
- **OXO** = Google Gemini (gemini-2.5-flash)
- **smurk** = OpenAI ChatGPT (gpt-4)

## 📁 Key Files (Clean Structure)
```
humanizer/
├── utils.py                      # Main interface (~85 lines)
└── llm_engines/                  # LLM module
    ├── prompts.py                # Shared AI prompts
    ├── gemini_engine.py          # OXO integration
    └── openai_engine.py          # smurk integration
```

## 🔑 Environment Variables (.env)
```bash
OFFLINE_MODE=False
DEBUG=True
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
```

## 📦 Critical Dependencies
```
openai==1.12.0
httpx==0.24.1
httpcore==0.17.3
google-generativeai==0.8.3
```

## 🔧 Troubleshooting

### OpenAI "proxies" error?
```powershell
pip install openai==1.12.0 httpx==0.24.1 --force-reinstall
```

### Server won't start?
```powershell
# Kill port 8000
$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    $pids = $conn | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique
    foreach ($pid in $pids) { Stop-Process -Id $pid -Force }
}
```

### Import errors?
```powershell
# Test imports
python -c "from humanizer.utils import humanize_text; print('OK')"
```

## 📝 How It Works

1. User selects **OXO** or **smurk** from dropdown
2. Enters text and clicks **Humanize**
3. `humanizer/views.py` receives request
4. Calls `humanize_text_with_engine(text, engine)`
5. Routes to `GeminiEngine` or `OpenAIEngine`
6. Engine sends text + prompts to API
7. API returns humanized text
8. Result displayed to user

## ⚠️ Important Notes

- ✅ **ALL humanization via APIs** - no local processing
- ✅ **Same prompts for both engines** - defined in `prompts.py`
- ✅ **Version locked** - openai 1.12.0 required for compatibility
- ✅ **Clean errors** - meaningful messages when things fail
- ✅ **Type hints** - full IDE support

## 📚 Documentation
- `FILE_STRUCTURE.md` - Complete architecture explanation
- `humanizer/llm_engines/README.md` - LLM module details
- Each `.py` file has docstrings

## 🧪 Test It
```powershell
# 1. Start server
python manage.py runserver 127.0.0.1:8000

# 2. Open browser
http://127.0.0.1:8000/humanizer/

# 3. Login
admin@example.com / admin1234

# 4. Test both engines
- Select OXO, paste text, click Humanize
- Select smurk, paste same text, click Humanize
- Compare outputs
```

## 🎯 Next Steps

### For Testing
- [ ] Test OXO with different text types
- [ ] Test smurk with different text types
- [ ] Compare output quality
- [ ] Check error handling (invalid API key, etc.)

### For Production
- [ ] Set `OFFLINE_MODE=False` in .env
- [ ] Configure PostgreSQL `DATABASE_URL`
- [ ] Set up proper SMTP for emails
- [ ] Add production API keys
- [ ] Update `ALLOWED_HOSTS` in settings.py

### For Enhancement
- [ ] Add response caching
- [ ] Add usage tracking
- [ ] Add A/B testing for prompts
- [ ] Add cost monitoring
- [ ] Add rate limiting

## 💡 Tips
- **Check server logs** for detailed error messages
- **Use admin account** for unlimited quota
- **Read docstrings** in code for usage examples
- **Update prompts** in one place (`prompts.py`)
- **Add new engines** by creating new file in `llm_engines/`
