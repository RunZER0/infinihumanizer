# Required Render Environment Variables

Set these in your Render dashboard: **Service → Environment**

## Database
```
DATABASE_URL=postgresql://postgres.lbgowbtsxonniutjxcmv:YOUR_PASSWORD@aws-1-us-east-2.pooler.supabase.com:6543/postgres?sslmode=require
```

## API Keys
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
DEEPSEEK_API_KEY=sk-xxxxx
```

## Django
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.infiniaihumanizer.live,.onrender.com
```

## Gunicorn Performance (Optional - for DeepSeek timeout issues)
```
GUNICORN_TIMEOUT=120
GUNICORN_WORKERS=2
```

**Note**: If DeepSeek continues timing out, set `GUNICORN_TIMEOUT=120` to give it more time. The default is 30s which is too short for slower API responses.

## After Setting Variables
1. Click **Save Changes**
2. Render will automatically redeploy
3. Check logs for successful startup
