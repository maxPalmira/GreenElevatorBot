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

# Check if we're linked to a Railway project
if ! railway whoami &>/dev/null; then
    echo "❌ Not logged into Railway. Please run 'railway login' first."
    exit 1
fi

# Ensure we're linked to the correct project
if ! railway status &>/dev/null; then
    echo "❌ Not linked to a Railway project. Please run 'railway link' first."
    exit 1
fi

# Get the Railway domain from environment
RAILWAY_DOMAIN="greenelevetortelegrambottest-production.up.railway.app"
if [ -z "$RAILWAY_DOMAIN" ]; then
    echo "❌ Could not determine Railway domain"
    exit 1
fi

echo "Deploying to Railway..."
echo "Target URL: https://$RAILWAY_DOMAIN"

# Deploy using the Railway CLI and capture the output
echo "Starting deployment and capturing build logs..."
railway up 2>&1 | tee deployment.log

# Check if deployment was successful
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "❌ Deployment failed! Check deployment.log for details"
    exit 1
fi

# Extract build URL from logs if present
BUILD_URL=$(grep -o 'https://railway.app/project/.*' deployment.log | head -n 1)
if [ ! -z "$BUILD_URL" ]; then
    echo "Build logs available at: $BUILD_URL"
fi

# Wait for deployment to complete and service to be available
echo "Waiting for service to be available..."
max_attempts=10
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -s "https://$RAILWAY_DOMAIN/health" | grep -q "ok"; then
        echo "✅ Service is responding"
        break
    fi
    echo "Attempt $attempt/$max_attempts: Service not ready yet..."
    sleep 10
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Service failed to respond after $max_attempts attempts"
    exit 1
fi

# Check webhook status
echo "Checking webhook status..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"

# Set webhook
echo -e "\nSetting webhook..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
  -d "url=https://$RAILWAY_DOMAIN/webhook"

echo -e "\nDeployment complete. Verify in Railway dashboard:"
echo "https://railway.app/project"

# Final health check
echo -e "\nFinal health check:"
curl -s "https://$RAILWAY_DOMAIN/health" 