#!/bin/bash

set -e

echo "Starting Skyhawk services with Docker Compose..."
docker-compose -f docker-compose.v2.yml up -d

echo "Waiting for services to be healthy..."
sleep 10

echo "Checking service status..."
docker-compose -f docker-compose.v2.yml ps

echo ""
echo "Services are running!"
echo "- ML Service: http://localhost:5001"
echo "- API Service: http://localhost:5002"
echo "- Agent Service: http://localhost:5003"
echo "- PostgreSQL: localhost:5432"
echo ""
echo "View logs: docker-compose -f docker-compose.v2.yml logs -f"
echo "Stop services: docker-compose -f docker-compose.v2.yml down"
