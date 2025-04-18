# Green Elevator Bot - Script Reference Guide

## Deployment Scripts

### `deploy.sh`
- **Purpose**: Deploys the application to Railway with comprehensive status tracking
- **Usage**: `./deploy.sh`
- **Description**: 
  - Authenticates with Railway
  - Deploys the application with detailed status tracking
  - Monitors deployment process in real-time
  - Detects deployment failures (including healthcheck failures)
  - Sets up webhooks
  - Runs comprehensive health check after deployment
  - Provides detailed deployment summary and troubleshooting tips

## Health Check Scripts

### `health_check.py` (Comprehensive Health Check)
- **Purpose**: Complete system and deployment status check
- **Usage**: `./health_check.py [options]`
- **Options**:
  - `--token <BOT_TOKEN>`: Specify bot token
  - `--url <URL>`: Specify application URL
  - `--json`: Output in JSON format
  - `--check-deployment`: Check deployment status (automatic for 'all' or 'deployment' components)
  - `--component {database,application,webhook,deployment,deployment-only,all}`: Check specific component
- **Description**: Consolidated health check tool that checks:
  - PostgreSQL database connection and schema (with record counts)
  - Application health (via health endpoint)
  - Telegram webhook status
  - Railway deployment status
  - Application uptime as stability indicator
  - Provides color-coded status indicators and troubleshooting tips

### `test_pg_connection.py`
- **Purpose**: Quick PostgreSQL connection test
- **Usage**: `./test_pg_connection.py`
- **Description**: Simple connection test to verify database access

## Webhook Testing

### `webhook_logger.py`
- **Purpose**: Test webhooks by sending commands to your bot
- **Usage**: `./webhook_logger.py <webhook_url> <user_id> <command> [options]`
- **Options**:
  - `--token <TOKEN>`: Bot token for sending notification messages
  - `--callback`: Send as callback query instead of message
  - `--verbose`: Show detailed request/response info
  - `--timeout <SECONDS>`: Set request timeout (default: 30s)
- **Example**: `./webhook_logger.py https://your-app.up.railway.app/webhook 123456789 "/start" --token YOUR_BOT_TOKEN`

## Common Tasks Quick Reference

### Deploy the bot
```bash
# Full deployment with status tracking
./deploy.sh
```

### Check deployment status
```bash
# Interactive deployment status check (recommended)
./check_deployment.sh

# Quick focused deployment status check
./health_check.py --component deployment-only

# Detailed deployment check
./health_check.py --component deployment
```

### Check overall system health
```bash
# Full system health check with deployment info
./health_check.py

# Check health and save JSON report
./health_check.py --json > health_report.json
```

### Check specific components
```bash
# Database status
./health_check.py --component database

# Webhook status
./health_check.py --component webhook

# Deployment status (detailed)
./health_check.py --component deployment
```

### Test webhook manually
```bash
# Send a test command
./webhook_logger.py https://your-app.up.railway.app/webhook YOUR_USER_ID "/start" --token YOUR_BOT_TOKEN

# Send a callback query (simulate button press)
./webhook_logger.py https://your-app.up.railway.app/webhook YOUR_USER_ID "some_callback_data" --callback --token YOUR_BOT_TOKEN
```

## Important Notes

### Railway Logs Warning

⚠️ **Do not use `railway logs` directly in scripts or Cursor**

The `railway logs` command streams continuous logs and waits for input (Ctrl+C to exit), which can hang Cursor or scripts. Instead:

1. Use `./health_check.py` which safely checks status without streaming logs
2. Use the Railway dashboard for live log viewing: https://railway.app/project
3. If needed, use a timeout: `timeout 5s railway logs`

### Railway Deployment Status Limitation

⚠️ **Railway CLI has limited deployment status visibility**

Due to Railway CLI limitations, our scripts can't always detect:
1. Failed healthchecks
2. Network failures during deployment
3. Detailed deployment history

For complete deployment status, always check the Railway dashboard.