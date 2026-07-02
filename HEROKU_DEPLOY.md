# 🚀 Star AI - 24/7 Heroku Deployment

## ⚡ Quickstart (5 minutes)

### 1. Install Heroku CLI
https://devcenter.heroku.com/articles/heroku-cli

### 2. Run deployment script
```bash
chmod +x deploy-heroku.sh
./deploy-heroku.sh
```

The script will:
- ✅ Create Heroku app
- ✅ Set environment variables
- ✅ Deploy bot
- ✅ Start 24/7 service

---

## Manual Setup

### Step 1: Create app
```bash
heroku login
heroku create your-app-name
```

### Step 2: Set secrets
```bash
heroku config:set \
  TELEGRAM_BOT_TOKEN="your_token" \
  OWNER_ID="your_id" \
  REQUIRED_CHANNEL="@channel" \
  REQUIRED_CHANNEL_LINK="https://t.me/channel"
```

### Step 3: Deploy
```bash
heroku git:remote -a your-app-name
git push heroku main
```

### Step 4: Monitor
```bash
heroku logs -a your-app-name -f
```

---

## 📊 Plans & Pricing

| Plan | Price | Uptime | Setup |
|------|-------|--------|-------|
| **Free** | $0 | ~18hrs/month (sleeps) | 5 min |
| **Standard 1x** | $7/mo | 24/7 ✅ | 5 min |
| **Standard 2x** | $50/mo | 24/7 + fast | 5 min |

💡 **Recommended**: Start free, upgrade to Standard 1x ($7/mo) for 24/7

---

## Upgrade to 24/7 (Always-On)

### Free tier sleeps after 30 mins. Upgrade:

```bash
heroku dyno:type standard-1x -a your-app-name
```

Or via dashboard: https://dashboard.heroku.com/apps

---

## 🛠️ Common Commands

```bash
# View logs
heroku logs -a your-app-name -f

# Restart bot
heroku restart -a your-app-name

# View environment variables
heroku config -a your-app-name

# Update a variable
heroku config:set VAR=value -a your-app-name

# View app status
heroku ps -a your-app-name

# Metrics
heroku metrics -a your-app-name
```

---

## 🔄 Update Bot After Deployment

```bash
# Make changes
git add .
git commit -m "Update feature"

# Deploy
git push heroku main

# Watch deployment
heroku logs -a your-app-name -f
```

---

## ❌ Troubleshooting

### Bot not responding?
```bash
# Check status
heroku ps -a your-app-name

# Restart
heroku restart -a your-app-name

# View errors
heroku logs -a your-app-name --tail=100
```

### App crashing?
```bash
# Full logs with errors
heroku logs -a your-app-name -n 500
```

### Missing packages?
```bash
# Rebuild and redeploy
git commit --allow-empty -m "Rebuild"
git push heroku main
```

---

## Alternative 24/7 Hosting

- **Railway.app** - Similar to Heroku, free tier
- **Replit** - Web-based, free 24/7
- **DigitalOcean** - $4+/mo, more control
- **AWS/Azure** - Free tier with 750 hours/mo

---

## 🎉 Done!

Your Star AI bot is now running 24/7 on Heroku! Monitor it anytime:

```bash
heroku logs -a your-app-name -f
```

---

**Questions?** Check Heroku docs: https://devcenter.heroku.com
