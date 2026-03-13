# Deployment Guide

## Deploy to Vercel (Recommended - Free)

### Prerequisites
- Vercel account: https://vercel.com
- Vercel CLI: `npm i -g vercel`

### Quick Deploy

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy**
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? Press Enter (uses repo name)
- Directory? Press Enter (current directory)
- Override settings? **N**

4. **Add Environment Variables**

After first deployment, add your secrets:
```bash
vercel env add OPENAI_API_KEY
```
Paste your OpenAI API key when prompted.

Also add:
```bash
vercel env add OPENAI_MODEL
# Enter: gpt-3.5-turbo
```

5. **Redeploy with Secrets**
```bash
vercel --prod
```

Your app is now live! 🚀

---

## Alternative: Deploy to Railway

Railway supports full-stack apps with persistent storage.

1. **Install Railway CLI**
```bash
npm i -g @railway/cli
```

2. **Login**
```bash
railway login
```

3. **Initialize Project**
```bash
railway init
```

4. **Add Environment Variables**
```bash
railway variables set OPENAI_API_KEY=your_key_here
railway variables set OPENAI_MODEL=gpt-3.5-turbo
```

5. **Deploy**
```bash
railway up
```

---

## Alternative: Deploy to Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt && npm install && npm run build`
   - **Start Command**: `npm run dev:all`
   - **Environment Variables**:
     - `OPENAI_API_KEY`: your key
     - `OPENAI_MODEL`: gpt-3.5-turbo

5. Click "Create Web Service"

---

## Environment Variables Needed

For any deployment platform, set these:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo
UPLOAD_API_KEY=                     (optional)
```

---

## Production Checklist

- ✅ Add environment variables on hosting platform
- ✅ Ensure `.env` is in `.gitignore` (already done)
- ✅ Test chatbot functionality after deployment
- ✅ Check file upload works
- ✅ Verify storage persistence (Railway/Render only)

---

## Troubleshooting

**"Backend not reachable"**
- Check environment variables are set on platform
- Verify API routes are correct
- Check platform logs for errors

**Vercel serverless timeout**
- Vercel free tier has 10s timeout
- Use Railway or Render for longer operations

**File storage**
- Vercel is stateless (files don't persist)
- Use Railway/Render for persistent file storage
- Or integrate S3/CloudFlare R2 for production storage
