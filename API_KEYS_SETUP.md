# API Keys Setup Guide

## 🚨 CRITICAL: Your humanizer won't work without API keys!

The error you're seeing ("it dissapears before i capture it") is caused by **missing AI API keys**.

## Quick Fix

1. **Copy `.env.example` to `.env`**:
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Get your API keys** (you need at least ONE):

   ### Option 1: Gemini (FREE - Recommended for testing)
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key
   - Free tier: 60 requests per minute!

   ### Option 2: OpenAI (Paid)
   - Visit: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Requires payment setup

   ### Option 3: DeepSeek (Affordable)
   - Visit: https://platform.deepseek.com/api_keys
   - Create an account
   - Generate API key
   - Very affordable pricing

3. **Edit `.env` file** and paste your keys:
   ```env
   GEMINI_API_KEY=AIzaSyD...your-actual-key-here
   OPENAI_API_KEY=sk-...your-actual-key-here  
   DEEPSEEK_API_KEY=sk-...your-actual-key-here
   ```

4. **Restart the Django server**:
   ```powershell
   # Press Ctrl+C to stop current server
   python manage.py runserver
   ```

## Testing Your Setup

After adding keys, run the diagnostic:
```powershell
python test_api_engines.py
```

This will:
- ✅ Check if API keys are configured
- ✅ Test connection to each AI engine
- ✅ Show you which engines are working

## What Happens Without API Keys?

The engine code checks for API keys on initialization:

```python
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set")
```

This `RuntimeError` is what's flashing on your screen!

## Minimum Requirements

You only need **ONE working API key** to use the humanizer:
- The frontend lets users select which engine to use
- If you only have Gemini key, just use Gemini engine
- Each engine has different strengths (see PROMPTS_GUIDE.md)

## Security Note

**NEVER commit `.env` to git!**
- `.env` is already in `.gitignore`
- Keep your API keys private
- The `.env.example` file shows the structure without real keys

## Still Having Issues?

Run the diagnostic and look for:
- ❌ "NOT SET" → API key missing
- ❌ "FAILED" + error message → Invalid key or network issue
- ✅ "SUCCESS" → That engine is working!

---

**Need help?** Check the full traceback when running `python test_api_engines.py`
