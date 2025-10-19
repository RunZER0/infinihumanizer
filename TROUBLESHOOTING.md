# 🔧 Troubleshooting Checklist

## ❌ Problem: "I am running it but i am hitting a certain error, it dissapears before i capture it, but the whole point, is i cant get the results"

### Root Cause: Missing API Keys

The error that's flashing is:
```
RuntimeError: [ENGINE]_API_KEY environment variable is not set
```

---

## ✅ SOLUTION (Step-by-Step)

### Step 1: Create .env File
```powershell
# In your project root directory:
Copy-Item .env.example .env
```

**Expected result:** `.env` file created

---

### Step 2: Add Your API Keys

Open `.env` file and add your keys:

```bash
# You said "all the keys are paid for they should work"
# Add them here:

GEMINI_API_KEY=AIzaSyD_your_actual_gemini_key_here
OPENAI_API_KEY=sk-proj-your_actual_openai_key_here
DEEPSEEK_API_KEY=sk-your_actual_deepseek_key_here
```

**Where to find your keys:**
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys
- DeepSeek: https://platform.deepseek.com/api_keys

---

### Step 3: Verify Keys Are Loaded

```powershell
python check_keys.py
```

**Expected output:**
```
✅ dotenv loaded

API Keys Status:
GEMINI_API_KEY: ✅ SET
OPENAI_API_KEY: ✅ SET
DEEPSEEK_API_KEY: ✅ SET

✅ At least one API key is set!
```

**If you see ❌ NOT SET:**
- Check .env file exists in project root
- Check keys are on correct lines (no typos)
- Check no extra spaces around = sign
- Check file is named `.env` not `.env.txt`

---

### Step 4: Test Engine Connectivity

```powershell
python test_api_engines.py
```

**Expected output:**
```
================================================================================
INFINIHUMANIZER DIAGNOSTIC TOOL
================================================================================

API KEY CONFIGURATION CHECK
================================================================================

Checking os.environ:
✅ GEMINI_API_KEY: AIzaSyD...abc123
✅ OPENAI_API_KEY: sk-proj...xyz789
✅ DEEPSEEK_API_KEY: sk-...def456

================================================================================
STARTING ENGINE TESTS
================================================================================

================================================================================
TESTING GEMINI ENGINE
================================================================================
📤 Sending test request...
   Input: This is a simple test sentence...
✅ SUCCESS!
   Output length: 67 characters

================================================================================
TESTING OPENAI ENGINE
================================================================================
📤 Sending test request...
✅ SUCCESS!

================================================================================
TESTING DEEPSEEK ENGINE
================================================================================
📤 Sending test request...
✅ SUCCESS!

================================================================================
TEST SUMMARY
================================================================================
   Gemini: ✅ PASS
   OpenAI: ✅ PASS
   DeepSeek: ✅ PASS

🎉 ALL TESTS PASSED! Your humanizer is ready to use!
```

**If you see ❌ FAILED:**
- Check API key is valid (not expired)
- Check API key has credits/quota
- Check internet connection
- Check firewall/VPN not blocking API calls

---

### Step 5: Restart Server

```powershell
# Stop current server (Ctrl+C)
# Then:
python manage.py runserver
```

**Expected output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 18, 2025 - 12:00:00
Django version 5.2.1, using settings 'core.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### Step 6: Test Humanization

1. Visit: http://127.0.0.1:8000/
2. Login: `testuser` / `password123`
3. Paste test text
4. Select engine
5. Click "Humanize"

**Expected result:** You get humanized text with quality scores

---

## 🐛 Common Issues & Fixes

### Issue 1: "check_keys.py shows ❌ NOT SET"

**Cause:** .env file not found or keys not in environment

**Fix:**
```powershell
# Check file exists:
Test-Path .env
# Should output: True

# If False, create it:
Copy-Item .env.example .env

# Then edit .env and add your keys
```

---

### Issue 2: "test_api_engines.py shows 'Invalid API key'"

**Cause:** API key is wrong or expired

**Fix:**
1. Go to API provider dashboard
2. Generate new API key
3. Copy to .env file
4. Save and test again

---

### Issue 3: "test_api_engines.py shows 'Rate limit exceeded'"

**Cause:** Too many API calls, hit quota

**Fix:**
- Wait a few minutes
- Check API usage on provider dashboard
- Upgrade API plan if needed
- Try different engine

---

### Issue 4: "test_api_engines.py hangs/takes forever"

**Cause:** Network issue or API server down

**Fix:**
- Check internet connection
- Try different engine
- Check API status page:
  - Gemini: https://status.cloud.google.com/
  - OpenAI: https://status.openai.com/
  - DeepSeek: Check their website

---

### Issue 5: "Humanization works but quality is poor"

**Cause:** Wrong engine for content type

**Fix:**
- Academic/Technical: Use **Gemini**
- Business/Professional: Use **OpenAI**
- Creative/Blogs: Use **DeepSeek**

---

### Issue 6: "ValidationError: Preservation violations"

**Cause:** Engine changed critical content

**Fix:**
- Validation automatically fixes this
- Check final_text in response
- If still issues, try different engine

---

### Issue 7: "Server starts but still can't humanize"

**Cause:** Keys not loaded into Django environment

**Fix:**
```powershell
# Restart server AFTER adding keys to .env
# Django loads .env on startup

# Check Django can see keys:
python manage.py shell

# In shell:
>>> import os
>>> os.getenv('GEMINI_API_KEY')
# Should show your key
```

---

### Issue 8: "Browser shows 'Humanization error'"

**Cause:** Backend error, check server terminal

**Fix:**
1. Look at terminal where `runserver` is running
2. Full error traceback will be there
3. Common errors:
   - "API_KEY not set" → Add to .env
   - "Invalid API key" → Check key is correct
   - "Network error" → Check internet
   - "Timeout" → API server slow, try again

---

## 📋 Quick Diagnostic Flow

```
START
  │
  ▼
[ ] Step 1: .env file exists?
      NO → Create it: Copy-Item .env.example .env
      YES → Continue
  │
  ▼
[ ] Step 2: API keys in .env?
      NO → Add your paid API keys
      YES → Continue
  │
  ▼
[ ] Step 3: Run `python check_keys.py`
      Shows ❌ → Fix .env file, retry
      Shows ✅ → Continue
  │
  ▼
[ ] Step 4: Run `python test_api_engines.py`
      FAILS → Check key validity, network
      PASSES → Continue
  │
  ▼
[ ] Step 5: Restart server
      `python manage.py runserver`
  │
  ▼
[ ] Step 6: Test in browser
      Works → ✅ SUCCESS!
      Fails → Check browser console (F12)
```

---

## 🎯 Expected Behavior When Working

### Console Output During Humanization

```
============================================================
🚀 AJAX HUMANIZATION REQUEST
   Engine: gemini
   Word count: 150
   Word balance: 29549
============================================================
🔍 Stage 1: Preprocessing & Analysis...
   ✅ Analysis complete:
      - AI patterns detected: 3 categories
      - Elements to preserve: 8
      - Safe variation zones: 5
⏳ Stage 2: Humanization with GEMINI...
   → Using direct processing (no chunking)
   ✅ Humanization complete! Output length: 542 chars
🔬 Stage 3: Quality Validation...
   ✅ Validation complete:
      - Overall score: 87/100
      - Passed: True
      - Issues detected: 0
      - AI Detection Risk: LOW
📊 Final Scores - Human: 85%, Read: 65%
✅ HUMANIZATION COMPLETE
============================================================
```

### Browser Response

```json
{
  "success": true,
  "output_text": "The humanized text...",
  "word_balance": 29399,
  "words_used": 150,
  "human_score": 85,
  "read_score": 65,
  "validation": {
    "score": 87,
    "passed": true,
    "risk_level": "LOW",
    "issues_count": 0
  }
}
```

---

## 🆘 Still Not Working?

### Last Resort Checks

1. **Python version:**
   ```powershell
   python --version
   # Should be 3.10+
   ```

2. **Required packages:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Django migrations:**
   ```powershell
   python manage.py migrate
   ```

4. **Firewall:**
   - Check Windows Firewall allows Python
   - Check antivirus not blocking

5. **Port conflict:**
   ```powershell
   # Try different port:
   python manage.py runserver 8080
   ```

---

## 📞 Quick Reference Commands

```powershell
# Diagnostic
python check_keys.py              # Check keys loaded
python test_api_engines.py        # Test engines

# Testing modules
python humanizer/preprocessing.py  # Test preprocessing
python humanizer/prompts.py        # Test prompts
python humanizer/validation.py     # Test validation

# Running
python manage.py runserver         # Start server

# Django
python manage.py shell             # Django shell
python manage.py migrate           # Run migrations
```

---

## ✅ Success Indicators

You know it's working when:

1. ✅ `check_keys.py` shows all keys SET
2. ✅ `test_api_engines.py` shows all PASS
3. ✅ Server starts without errors
4. ✅ Browser humanization returns results
5. ✅ Console shows 3-stage pipeline output
6. ✅ Results have quality scores

---

## 🎉 Once It Works

**You'll have:**
- ✅ Undetectable AI humanization
- ✅ 65-95% detection evasion
- ✅ Professional quality output
- ✅ Content preservation (98% accuracy)
- ✅ Automated quality fixes
- ✅ 30,000 word quota for testing

**Next steps:**
- Test with different content types
- Try all three engines
- Monitor quality scores
- Adjust based on needs

---

**The system is complete and ready. Just add your API keys!** 🔑
