#!/bin/bash
# Updated deploy.sh - Fixes Railway CLI commands according to official documentation

set -e

echo "==================================================="
echo "   GREEN ELEVATOR BOT - RAILWAY DEPLOYMENT SCRIPT"
echo "==================================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
    echo "✅ Loaded environment variables"
else
    echo "❌ .env file not found"
    exit 1
fi

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN not found in .env file"
    exit 1
fi

# Check if we're logged into Railway
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

# Store the deployment start time
DEPLOY_START_TIME=$(date +%s)

# Start deployment and capture the output
echo -e "\n📦 INITIATING DEPLOYMENT"
echo "=================================================="
echo "Starting deployment and capturing build logs..."
railway up --detach 2>&1 | tee deployment.log

# Extract deployment ID
DEPLOY_ID=$(grep -o "https://railway.com/project/.*" deployment.log | head -n 1 | sed 's/.*id=\([^&]*\).*/\1/')
if [ ! -z "$DEPLOY_ID" ]; then
    echo "🆔 Deployment ID: $DEPLOY_ID"
    echo "📊 Build logs available at: https://railway.app/project/deployments/$DEPLOY_ID"
fi

echo -e "\n🔄 TRACKING DEPLOYMENT STATUS"
echo "=================================================="
echo "Checking deployment status every 10 seconds..."
echo "Press Ctrl+C to stop monitoring (deployment will continue)"

MAX_CHECKS=30  # 5 minutes max waiting time
CHECK_INTERVAL=10  # seconds between checks

# Initialize flags
DEPLOYMENT_COMPLETED=false
DEPLOYMENT_SUCCESS=false
HEALTHCHECK_PASSED=false

for ((i=1; i<=MAX_CHECKS; i++)); do
    echo -e "\n📊 Status check attempt $i/$MAX_CHECKS"
    
    # Get deployment status in JSON format
    STATUS_JSON=$(railway status --json 2>/dev/null)
    if [ $? -ne 0 ]; then
        echo "⚠️ Could not get deployment status, will try again..."
        sleep $CHECK_INTERVAL
        continue
    fi
    
    # Extract status
    STATE=$(echo $STATUS_JSON | grep -o '"state":"[^"]*"' | head -1 | cut -d':' -f2 | tr -d '"')
    
    if [ "$STATE" == "RUNNING" ]; then
        echo "✅ Deployment succeeded! Service is running."
        DEPLOYMENT_COMPLETED=true
        DEPLOYMENT_SUCCESS=true
        break
    elif [ "$STATE" == "FAILED" ] || [ "$STATE" == "ERROR" ]; then
        echo "❌ Deployment failed!"
        DEPLOYMENT_COMPLETED=true
        break
    else
        echo "⏳ Deployment still in progress... Current state: $STATE"
    fi
    
    # Check for network errors or healthcheck failures
    HEALTH_STATUS=$(railway list deployments --json 2>/dev/null | grep -E '"status"|"healthcheckFailed"' | head -3)
    if echo "$HEALTH_STATUS" | grep -q '"healthcheckFailed":true'; then
        echo "❌ Healthcheck failed during deployment!"
        DEPLOYMENT_COMPLETED=true
        break
    fi
    
    # Try to get health status from new deployment
    HEALTH_RESPONSE=$(curl -s "https://$RAILWAY_DOMAIN/health")
    if [[ "$HEALTH_RESPONSE" == *"OK"* || "$HEALTH_RESPONSE" == *"status"* ]]; then
        echo "✅ Health endpoint is responding. Service appears to be online."
        HEALTHCHECK_PASSED=true
    else
        echo "⏳ Health endpoint not responding yet."
    fi
    
    # Skip the rest of waiting if we've confirmed the health endpoint is responding
    if [ "$HEALTHCHECK_PASSED" == true ] && [ "$i" -gt 5 ]; then
        echo "✅ Health check passed, deployment seems successful!"
        DEPLOYMENT_SUCCESS=true
        DEPLOYMENT_COMPLETED=true
        break
    fi
    
    # Wait before next check
    sleep $CHECK_INTERVAL
done

# Calculate deployment time
DEPLOY_END_TIME=$(date +%s)
DEPLOY_DURATION=$((DEPLOY_END_TIME - DEPLOY_START_TIME))
DEPLOY_MINUTES=$((DEPLOY_DURATION / 60))
DEPLOY_SECONDS=$((DEPLOY_DURATION % 60))

echo -e "\n⏱️ Deployment process took $DEPLOY_MINUTES minutes and $DEPLOY_SECONDS seconds."

if [ "$DEPLOYMENT_COMPLETED" == false ]; then
    echo "⚠️ Deployment status monitoring timed out after $((MAX_CHECKS * CHECK_INTERVAL)) seconds."
    echo "Check Railway dashboard for current status: https://railway.app/project"
fi

echo -e "\n🔗 SETTING UP WEBHOOK"
echo "=================================================="
# Check webhook status
echo "Checking current webhook status..."
WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo")

# Check if the webhook is already set correctly
if [[ "$WEBHOOK_INFO" == *"\"url\":\"https://$RAILWAY_DOMAIN/webhook\""* ]]; then
    echo "✅ Webhook already set correctly to https://$RAILWAY_DOMAIN/webhook"
else
    # Set webhook
    echo "Setting webhook to https://$RAILWAY_DOMAIN/webhook..."
    WEBHOOK_RESULT=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
      -d "url=https://$RAILWAY_DOMAIN/webhook")
      
    if [[ "$WEBHOOK_RESULT" == *"\"ok\":true"* ]]; then
        echo "✅ Webhook set successfully!"
    else
        echo "❌ Failed to set webhook: $WEBHOOK_RESULT"
    fi
fi

echo -e "\n🏥 RUNNING COMPREHENSIVE HEALTH CHECK"
echo "=================================================="
# Run health check
if [ -f "./health_check.py" ]; then
    echo "Running health check..."
    python3 ./health_check.py
else
    echo "❌ health_check.py not found. Skipping comprehensive health check."
fi

echo -e "\n📋 DEPLOYMENT SUMMARY"
echo "=================================================="
if [ "$DEPLOYMENT_SUCCESS" == true ]; then
    echo "✅ DEPLOYMENT STATUS: SUCCESS"
else
    if [ "$DEPLOYMENT_COMPLETED" == true ]; then
        echo "❌ DEPLOYMENT STATUS: FAILED"
    else
        echo "⚠️ DEPLOYMENT STATUS: UNKNOWN (monitoring timed out)"
    fi
fi

echo -e "\nWebhook URL: https://$RAILWAY_DOMAIN/webhook"
echo "Application URL: https://$RAILWAY_DOMAIN"
echo "Health endpoint: https://$RAILWAY_DOMAIN/health"

if [ "$DEPLOYMENT_SUCCESS" == false ]; then
    echo -e "\n⚠️ TROUBLESHOOTING TIPS:"
    echo "1. Check Railway dashboard for detailed error logs"
    echo "2. Run './health_check.py' for a comprehensive health check"
    echo "3. Check your most recent code changes for potential issues"
    echo "4. Run 'railway logs' to view application logs"
    echo "5. Railway deployment may be retrying - check dashboard"
fi

echo -e "\nRailway dashboard: https://railway.app/project" 