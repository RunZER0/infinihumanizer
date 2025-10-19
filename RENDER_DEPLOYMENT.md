# 🚀 RENDER DEPLOYMENT GUIDE

## Prerequisites
- GitHub account with your repository
- Render account (free tier works)
- API keys for OpenAI, DeepSeek (and optionally Gemini)
- Paystack account (if using payment features)
- Brevo/Sendinblue account (for email functionality)

## 📋 Deployment Checklist

### 1. Prepare Your Repository

✅ **Files Created:**
- `Procfile` - Gunicorn web server configuration
- `runtime.txt` - Python version specification
- `build.sh` - Build script for migrations and static files
- `.env.example` - Template for environment variables
- `.gitignore` - Updated to exclude sensitive files

✅ **Before Pushing to GitHub:**
```bash
# Make sure you're in the project directory
cd c:\Users\USER\Documents\infinihumanizer-20251012T154805Z-1-001\infinihumanizer

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Add your remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### 2. Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** `infinihumanizer-db`
   - **Database:** `infinihumanizer`
   - **User:** (auto-generated)
   - **Region:** Choose closest to your users
   - **Plan:** Free tier is fine for testing
4. Click **"Create Database"**
5. **Save the Internal Database URL** - you'll need this for your web service

### 3. Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `infinihumanizer`
   - **Region:** Same as your database
   - **Branch:** `main`
   - **Root Directory:** (leave blank if at repo root, or set to `infinihumanizer` if nested)
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn core.wsgi:application`
   - **Plan:** Free tier to start

### 4. Configure Environment Variables

In your Render web service settings, add these environment variables:

#### **Required Variables:**

```bash
# Django
DJANGO_SECRET_KEY=<generate-secure-key>
DEBUG=False
OFFLINE_MODE=False

# Database (use Internal Database URL from step 2)
DATABASE_URL=<your-render-postgres-internal-url>

# AI API Keys (REQUIRED)
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-claude-key>
DEEPSEEK_API_KEY=<your-deepseek-key>
GEMINI_API_KEY=<your-gemini-key-optional>

# Payment (Paystack)
PAYSTACK_PUBLIC_KEY=<your-paystack-public-key>
PAYSTACK_SECRET_KEY=<your-paystack-secret-key>

# Email (Brevo/Sendinblue)
EMAIL_HOST_USER=<your-brevo-email>
EMAIL_HOST_PASSWORD=<your-brevo-smtp-password>
DEFAULT_FROM_EMAIL=Infiniai <noreply@yourdomain.com>
```

#### **Generate Secure Django Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Update Domain Settings (After Deployment)

Once deployed, Render will give you a URL like: `https://infinihumanizer.onrender.com`

**If you already have the domain configured in settings.py** (which you do: `infinihumanizer.onrender.com`), you're good to go!

If you want to use a custom domain:
1. Add it in Render dashboard under "Custom Domain"
2. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` in `settings.py`
3. Push changes to GitHub (Render will auto-redeploy)

### 6. Deploy!

1. Click **"Create Web Service"**
2. Render will:
   - Pull your code from GitHub
   - Install dependencies from `requirements.txt`
   - Run `build.sh` (downloads NLTK data, collects static files, runs migrations)
   - Start Gunicorn server
3. Monitor the logs for any errors

### 7. Verify Deployment

Once deployed, test these endpoints:
- `https://your-app.onrender.com/` - Homepage
- `https://your-app.onrender.com/accounts/login/` - Login page
- `https://your-app.onrender.com/humanizer/` - Humanizer interface

## 🔧 Troubleshooting

### Build Fails
- Check logs in Render dashboard
- Verify `build.sh` has execute permissions
- Ensure all packages in `requirements.txt` are available

### Static Files Not Loading
- Verify `STATIC_ROOT` in settings.py
- Check `collectstatic` ran successfully in build logs
- WhiteNoise should handle static files automatically

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check database is in same region as web service
- Use **Internal Database URL** not External

### NLTK Data Missing
- Build script downloads `punkt` and `punkt_tab`
- Check build logs to confirm download succeeded
- May need to add timeout or retry logic if download fails

### SSL/HTTPS Issues
- Render provides free SSL automatically
- Ensure `SECURE_SSL_REDIRECT=True` in production
- `CSRF_COOKIE_SECURE=True` and `SESSION_COOKIE_SECURE=True` should be enabled

## 📊 Monitoring

- **Logs:** View in Render dashboard → Your Service → Logs
- **Metrics:** Monitor CPU, memory, and bandwidth usage
- **Alerts:** Set up notifications for downtime

## 🔄 Continuous Deployment

Render automatically redeploys when you push to your GitHub repository:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will:
1. Detect the push
2. Pull latest code
3. Run build script
4. Restart service with zero downtime

## 💰 Cost Considerations

**Free Tier Limits:**
- Web services spin down after 15 minutes of inactivity
- First request after spindown takes ~30 seconds (cold start)
- 750 hours/month free
- 512 MB RAM

**Upgrade to Paid ($7/month):**
- Always-on (no cold starts)
- More RAM and CPU
- Better for production use

## 🔐 Security Checklist

✅ `DEBUG=False` in production
✅ Secure `SECRET_KEY` generated
✅ `.env` file in `.gitignore`
✅ API keys stored in environment variables
✅ SSL/HTTPS enabled
✅ CSRF protection enabled
✅ Database credentials not in code

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)

---

## 🎉 You're Ready!

Your project is now configured for Render deployment. Follow the steps above and you'll be live in minutes!
