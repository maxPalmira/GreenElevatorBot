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

# Start deployment and capture the output
echo "Starting deployment and capturing build logs..."
railway up 2>&1 | tee deployment.log

# Extract build URL from logs if present
BUILD_URL=$(grep -o 'https://railway.app/project/.*' deployment.log | head -n 1)
if [ ! -z "$BUILD_URL" ]; then
    echo "Build logs available at: $BUILD_URL"
fi

echo "Deployment initiated. Waiting for stages to complete..."

# Function to check deployment status
check_deployment_status() {
    # This is a placeholder - we need to implement proper status checking
    # using Railway's API or CLI commands that can show deployment status
    echo "Checking deployment status..."
    echo "⚠️ Note: Currently unable to programmatically check deployment status"
    echo "Please check the Railway dashboard at: https://railway.app/project"
    echo "Current deployment stages:"
    echo "- Initialization"
    echo "- Build"
    echo "- Deploy > Creating containers"
    echo "- Network"
    echo "- Post-deploy"
}

# Wait for deployment to potentially complete
echo "Waiting 2 minutes for deployment to progress..."
for i in {1..12}; do
    echo "Checking status (attempt $i/12)..."
    check_deployment_status
    
    # Try to get health status from new deployment
    HEALTH_RESPONSE=$(curl -s "https://$RAILWAY_DOMAIN/health")
    if [[ $HEALTH_RESPONSE == *"initialization"* ]]; then
        echo "✅ New version detected! Enhanced health endpoint is responding"
        break
    else
        echo "⏳ Still waiting for new version... (old version still active)"
    fi
    
    sleep 10
done

echo "Deployment status check complete."
echo "⚠️ IMPORTANT: Please verify in the Railway dashboard that all stages completed successfully:"
echo "https://railway.app/project"

# Check webhook status
echo -e "\nChecking webhook status..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | python3 -m json.tool

# Set webhook
echo -e "\nSetting webhook..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
  -d "url=https://$RAILWAY_DOMAIN/webhook" | python3 -m json.tool

echo -e "\nDeployment process complete, but please:"
echo "1. Verify all deployment stages in Railway dashboard"
echo "2. Check that the new health endpoints are responding:"
echo "   curl https://$RAILWAY_DOMAIN/health"
echo "   curl https://$RAILWAY_DOMAIN/health/init"
echo "   curl https://$RAILWAY_DOMAIN/health/logs" 