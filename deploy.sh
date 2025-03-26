#!/bin/bash
# deploy.sh - Non-interactive Railway deployment script

echo "Starting non-interactive Railway deployment..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables"
else
    echo "❌ .env file not found"
    exit 1
fi

# Set Railway as the current project without interaction
export RAILWAY_TOKEN=$(cat ~/.railway/config.json | grep token | cut -d'"' -f4)

# Validate token
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "❌ Failed to extract Railway token. Please login with 'railway login' first."
    exit 1
else
    echo "✅ Railway token found"
fi

# Try to deploy using the Railway CLI with a timeout
echo "Deploying to Railway (with 30s timeout)..."
timeout 30 railway up > /dev/null 2>&1

# Check webhook status
echo "Checking webhook status..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"

# Set webhook
echo -e "\nSetting webhook..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
  -d "url=https://1greenelevatorbotprod-production.up.railway.app/webhook"

echo -e "\nDeployment initiated. Check Railway dashboard for status:"
echo "https://railway.app/project"
echo -e "\nTo manually set webhook after deployment is complete, run:"
echo "curl -s \"https://api.telegram.org/bot$BOT_TOKEN/setWebhook\" -d \"url=https://1greenelevatorbotprod-production.up.railway.app/webhook\"" 