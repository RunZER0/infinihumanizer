# 📋 PRE-DEPLOYMENT CHECKLIST

Use this checklist before pushing to GitHub and deploying to Render.

## ✅ Files Verification

- [x] `Procfile` exists
- [x] `runtime.txt` exists (Python 3.12.0)
- [x] `build.sh` exists and is executable
- [x] `requirements.txt` includes all dependencies
- [x] `.gitignore` properly configured
- [x] `.env.example` has all required variables
- [x] `RENDER_DEPLOYMENT.md` guide available

## ✅ Code Configuration

- [x] `core/settings.py` has all API key environment variables
- [x] `ALLOWED_HOSTS` includes your Render domain
- [x] `CSRF_TRUSTED_ORIGINS` includes your domain
- [x] Database configured for PostgreSQL in production
- [x] Static files configured with WhiteNoise
- [x] Security settings enabled (SSL, secure cookies)
- [x] `anthropic` package added to requirements.txt
- [x] Claude engine supports `ANTHROPIC_API_KEY`

## ⚠️ Before Pushing to GitHub

- [ ] **Remove any `.env` file** (should already be in .gitignore)
- [ ] **Check no API keys in code** (search for "sk-", "api_key")
- [ ] **Remove `db.sqlite3`** if it contains test data
- [ ] **Generate new Django SECRET_KEY** for production
- [ ] **Review `DEPLOYMENT_READY.md`** for instructions

## 🔑 API Keys to Obtain

Before deploying, make sure you have:

- [ ] **OpenAI API Key** - https://platform.openai.com/api-keys
- [ ] **Anthropic API Key** - https://console.anthropic.com/settings/keys
- [ ] **DeepSeek API Key** - https://platform.deepseek.com/api_keys
- [ ] **Paystack Keys** (if using payments)
- [ ] **Brevo SMTP credentials** (for email)

## 🚀 Render Setup Steps

- [ ] Create Render account
- [ ] Create PostgreSQL database on Render
- [ ] Save Internal Database URL
- [ ] Create Web Service
- [ ] Connect GitHub repository
- [ ] Set Build Command: `./build.sh`
- [ ] Set Start Command: `gunicorn core.wsgi:application`
- [ ] Add all environment variables in Render dashboard
- [ ] Deploy!

## 🧪 Post-Deployment Testing

After deployment, test:

- [ ] Homepage loads (`/`)
- [ ] Login page works (`/accounts/login/`)
- [ ] Humanizer interface loads (`/humanizer/`)
- [ ] Test DeepSeek (Loly) engine
- [ ] Test Claude (OXO) engine
- [ ] Test OpenAI (Smurk) engine
- [ ] Human reading score displays correctly
- [ ] Static files load (CSS, images)
- [ ] No console errors in browser
- [ ] Check Render logs for errors

## 📝 Git Commands Ready

```powershell
# Navigate to project directory
cd c:\Users\USER\Documents\infinihumanizer-20251012T154805Z-1-001\infinihumanizer

# Check status
git status

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Add remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

## 🎯 Environment Variables Template

Copy this template and fill in your actual values:

```bash
DJANGO_SECRET_KEY=
DEBUG=False
OFFLINE_MODE=False
DATABASE_URL=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
GEMINI_API_KEY=
PAYSTACK_PUBLIC_KEY=
PAYSTACK_SECRET_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

## ✨ You're Ready When...

✅ All checkboxes above are checked
✅ API keys are ready
✅ GitHub repo is ready to receive push
✅ You've reviewed `RENDER_DEPLOYMENT.md`

---

**Need help?** Check `RENDER_DEPLOYMENT.md` for detailed instructions!
