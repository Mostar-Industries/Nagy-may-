#!/bin/bash

set -e

echo "Setting up Skyhawk local environment..."

# Create .env from .env.local if it doesn't exist
if [ ! -f .env ]; then
    cp .env.local .env
    echo "Created .env from .env.local"
fi

# Create directories
mkdir -p logs snapshots

# Install Python dependencies for each service
echo "Installing ml_service dependencies..."
pip install -r ml_service/requirements.txt

echo "Installing capture_service dependencies..."
pip install -r capture_service/requirements.txt

echo "Installing MNTRK_API dependencies..."
cd MNTRK_API && pip install -r requirements.txt && cd ..

echo "Installing MNTRK_Agent_API dependencies..."
cd MNTRK_Agent_API && pip install -r requirements.txt && cd ..

echo "Setup complete! Run: docker-compose -f docker-compose.v2.yml up -d"
