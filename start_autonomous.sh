#!/usr/bin/env bash
# Autonomous Detection System Startup Script
# No manual uploads - full automation only

set -e

echo "================================================"
echo "  SKYHAWK AUTONOMOUS DETECTION SYSTEM"
echo "================================================"
echo ""
echo "Mode: FULLY AUTOMATED"
echo "Flow: RTSP --> Capture --> YOLO --> Database --> Map"
echo ""
echo "Starting services..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Navigate to backend
cd backend

# Start all services with docker-compose
echo "[1/4] Starting PostgreSQL database..."
docker-compose up -d postgres
sleep 5

echo "[2/4] Starting ML inference service..."
docker-compose up -d ml-service
sleep 10

echo "[3/4] Starting API services..."
docker-compose up -d api-service agent-service
sleep 5

echo "[4/4] Starting AUTONOMOUS CAPTURE SERVICE..."
docker-compose up -d capture-service

echo ""
echo "================================================"
echo "  ALL SERVICES STARTED!"
echo "================================================"
echo ""
echo "Capture Service: MONITORING RTSP STREAMS"
echo "ML Service: READY FOR INFERENCE"
echo "Database: STORING DETECTIONS"
echo "Frontend: http://localhost:5000/monitoring"
echo ""
echo "Detections will appear automatically on the map!"
echo ""
echo "Press Ctrl+C to stop following logs"
echo ""

# Follow logs
docker-compose logs -f capture-service

cd ..
