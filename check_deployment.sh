#!/bin/bash
# check_deployment.sh - Quick deployment status check with dashboard access
# Shows deployment status and opens Railway dashboard for detailed view

# Set text colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[1;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}==================================================${NC}"
echo -e "${BOLD}   GREEN ELEVATOR BOT - DEPLOYMENT STATUS CHECK   ${NC}"
echo -e "${BOLD}==================================================${NC}"

# Run quick deployment status check
echo -e "\n${CYAN}Running basic deployment status check...${NC}"

# Run health check with deployment-only flag
python3 ./health_check.py --component deployment-only

echo -e "\n${YELLOW}Note: The Railway dashboard will provide more complete information${NC}"
echo -e "${YELLOW}about deployment status, including healthcheck failures.${NC}"

# Ask if user wants to open Railway dashboard
echo -e "\n${BOLD}Would you like to open the Railway dashboard? (y/n)${NC}"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo -e "\n${CYAN}Opening Railway dashboard...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "https://railway.app/project"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        xdg-open "https://railway.app/project" &> /dev/null
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        start "https://railway.app/project"
    else
        echo -e "${YELLOW}Couldn't automatically open browser. Please visit:${NC}"
        echo -e "https://railway.app/project"
    fi
else
    echo -e "\n${CYAN}To view detailed deployment status later, visit:${NC}"
    echo -e "https://railway.app/project"
fi 