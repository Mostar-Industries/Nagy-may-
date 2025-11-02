#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Skyhawk Backend Endpoint Testing ===${NC}\n"

# Function to test endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -e "${YELLOW}Testing: $name${NC}"
    echo "URL: $url"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$url" -H "Content-Type: application/json" -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [[ $http_code == 200 ]] || [[ $http_code == 201 ]]; then
        echo -e "${GREEN}✓ SUCCESS (HTTP $http_code)${NC}"
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
    fi
    
    echo "Response: $body"
    echo ""
}

# Test ML Service
echo -e "\n${YELLOW}--- ML Service (Port 5001) ---${NC}\n"
test_endpoint "ML Health Check" "GET" "http://localhost:5001/health"
test_endpoint "Model Info" "GET" "http://localhost:5001/model/info"

# Test API Service
echo -e "\n${YELLOW}--- API Service (Port 5002) ---${NC}\n"
test_endpoint "API Documentation" "GET" "http://localhost:5002/ui/"
test_endpoint "Get Detections" "GET" "http://localhost:5002/detections?limit=5"

# Test Agent Service
echo -e "\n${YELLOW}--- Agent Service (Port 5003) ---${NC}\n"
test_endpoint "Agent Documentation" "GET" "http://localhost:5003/ui/"
test_endpoint "Get Alerts" "GET" "http://localhost:5003/agent/alerts"

# Test with sample image (if provided)
if [ -f "$1" ]; then
    echo -e "\n${YELLOW}--- Image Inference Tests ---${NC}\n"
    
    echo -e "${YELLOW}Testing: ML Service Image Detection${NC}"
    curl -X POST -F "image=@$1" http://localhost:5001/detect
    echo ""
    
    echo -e "${YELLOW}Testing: API Service Image Upload${NC}"
    curl -X POST -F "image=@$1" http://localhost:5002/predict
    echo ""
fi

echo -e "${GREEN}=== Testing Complete ===${NC}"
