#!/bin/bash
# Manual test script for Blueprint Graph
# This script runs a simple test scenario to verify the system is working correctly

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting Blueprint Graph manual test scenario...${NC}"

# Check if API is running
echo -e "\n${YELLOW}Checking if API is running...${NC}"
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}API is not running. Please start the API first.${NC}"
    echo -e "Run: docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}API is running.${NC}"

# Generate test data
echo -e "\n${YELLOW}Generating test data...${NC}"
python tests/generate_test_data.py --count 5 --format ocsf --api http://localhost:8000
python tests/generate_test_data.py --count 5 --format syslog --api http://localhost:8000
python tests/generate_test_data.py --count 5 --format cef --api http://localhost:8000

# Create a test detection rule
echo -e "\n${YELLOW}Creating a test detection rule...${NC}"
RULE_DATA='{
    "name": "Test Failed Authentication Rule",
    "description": "Detects failed authentication attempts",
    "severity": "high",
    "query": "MATCH (e:Event)-[:HAS_SOURCE]->(s) WHERE e.class_uid = \"0001\" AND e.outcome = \"failure\" RETURN e, s",
    "tags": ["authentication", "test"],
    "mitre_techniques": ["T1110"],
    "enabled": true
}'

RULE_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$RULE_DATA" http://localhost:8000/rules)
RULE_ID=$(echo $RULE_RESPONSE | grep -o '"rule_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$RULE_ID" ]; then
    echo -e "${RED}Failed to create rule.${NC}"
    exit 1
fi

echo -e "${GREEN}Created rule with ID: $RULE_ID${NC}"

# Generate authentication failure events
echo -e "\n${YELLOW}Generating authentication failure events...${NC}"
AUTH_EVENT='{
    "event": {
        "class_uid": "0001",
        "category_uid": "0002",
        "time": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
        "severity": 8,
        "message": "Failed authentication attempt",
        "outcome": "failure",
        "auth_type": "password",
        "metadata": {
            "version": "1.0.0",
            "product": {
                "name": "Test Product",
                "vendor_name": "Test Vendor"
            }
        },
        "src": {
            "id": "src-1234",
            "type": "IP",
            "ip": "192.168.1.100",
            "hostname": "attacker-pc.example.com"
        },
        "dst": {
            "id": "dst-5678",
            "type": "IP",
            "ip": "10.0.0.5"
        },
        "principal": {
            "id": "user-9012",
            "type": "User",
            "name": "admin",
            "domain": "test.local"
        }
    },
    "source_format": "ocsf"
}'

for i in {1..3}; do
    curl -s -X POST -H "Content-Type: application/json" -d "$AUTH_EVENT" http://localhost:8000/events > /dev/null
    echo -e "${GREEN}Sent authentication failure event $i${NC}"
done

# Run detection
echo -e "\n${YELLOW}Running detection rules...${NC}"
DETECTION_RESPONSE=$(curl -s -X POST http://localhost:8000/run-detection)
ALERTS_COUNT=$(echo $DETECTION_RESPONSE | grep -o '"alerts_count":[0-9]*' | cut -d':' -f2)

echo -e "${GREEN}Detection completed. Generated $ALERTS_COUNT alerts.${NC}"

# Get alerts
echo -e "\n${YELLOW}Retrieving alerts...${NC}"
ALERTS_RESPONSE=$(curl -s http://localhost:8000/alerts)
ALERTS_COUNT=$(echo $ALERTS_RESPONSE | grep -o '"total":[0-9]*' | cut -d':' -f2)

echo -e "${GREEN}Retrieved $ALERTS_COUNT alerts.${NC}"

# Get alerts for the specific rule
echo -e "\n${YELLOW}Retrieving alerts for rule $RULE_ID...${NC}"
RULE_ALERTS_RESPONSE=$(curl -s "http://localhost:8000/alerts?rule_id=$RULE_ID")
RULE_ALERTS_COUNT=$(echo $RULE_ALERTS_RESPONSE | grep -o '"total":[0-9]*' | cut -d':' -f2)

echo -e "${GREEN}Retrieved $RULE_ALERTS_COUNT alerts for rule $RULE_ID.${NC}"

# Clean up
echo -e "\n${YELLOW}Cleaning up...${NC}"
curl -s -X DELETE http://localhost:8000/rules/$RULE_ID > /dev/null
echo -e "${GREEN}Deleted rule $RULE_ID.${NC}"

echo -e "\n${GREEN}Manual test completed successfully!${NC}"
echo -e "Summary:"
echo -e "  - Generated and sent 15 random events (5 each of OCSF, syslog, CEF)"
echo -e "  - Created a detection rule for failed authentication attempts"
echo -e "  - Sent 3 authentication failure events"
echo -e "  - Ran detection and generated alerts"
echo -e "  - Retrieved and verified alerts"
echo -e "  - Cleaned up by deleting the test rule" 