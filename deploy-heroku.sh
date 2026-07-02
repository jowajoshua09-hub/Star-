#!/bin/bash
set -e

echo "🚀 Star AI Bot - Heroku 24/7 Deployment"
echo "======================================="

if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found"
    echo "Install: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "📝 Login to Heroku..."
heroku login

echo ""
read -p "Enter app name (or press Enter for random): " APP_NAME

if [ -z "$APP_NAME" ]; then
    APP_NAME="starai-$(date +%s)"
fi

echo "Creating app: $APP_NAME"
heroku create $APP_NAME || true

echo ""
echo "🔑 Setting environment variables..."
read -sp "TELEGRAM_BOT_TOKEN: " BOT_TOKEN
echo ""
read -p "OWNER_ID: " OWNER_ID
read -p "REQUIRED_CHANNEL (e.g., @startech372): " CHANNEL
read -p "REQUIRED_CHANNEL_LINK: " CHANNEL_LINK

heroku config:set -a $APP_NAME \
  TELEGRAM_BOT_TOKEN="$BOT_TOKEN" \
  OWNER_ID="$OWNER_ID" \
  REQUIRED_CHANNEL="$CHANNEL" \
  REQUIRED_CHANNEL_LINK="$CHANNEL_LINK"

echo ""
echo "Adding buildpacks..."
heroku buildpacks:add --index 1 heroku/python -a $APP_NAME

echo ""
echo "Setting up git remote..."
git remote remove heroku 2>/dev/null || true
heroku git:remote -a $APP_NAME

echo ""
echo "⬆️  Deploying..."
git push heroku main

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Dashboard: https://dashboard.heroku.com/apps/$APP_NAME"
echo "View logs: heroku logs -a $APP_NAME -f"
echo "Restart bot: heroku restart -a $APP_NAME"
echo ""
echo "🎉 Your bot is now running 24/7!"
