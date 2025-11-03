#!/bin/bash
# Setup script for Mastomys Detection Inference System

set -e

echo "🚀 Setting up Mastomys Detection Inference System"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Node.js
echo "1️⃣ Checking Node.js..."
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js $(node -v) found${NC}"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# 2. Check Python
echo ""
echo "2️⃣ Checking Python..."
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python $(python3 --version) found${NC}"
else
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# 3. Install Python dependencies
echo ""
echo "3️⃣ Installing Python dependencies..."
cd backend/ml_service
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate || . venv/Scripts/activate 2>/dev/null || true
pip install --quiet --upgrade pip
pip install --quiet ultralytics pillow numpy
echo -e "${GREEN}✓ Python dependencies installed${NC}"
cd ../..

# 4. Check YOLO model
echo ""
echo "4️⃣ Checking YOLO model..."
MODEL_PATH="backend/ml_service/models"
if [ ! -d "$MODEL_PATH" ]; then
    mkdir -p "$MODEL_PATH"
fi

if [ -f "$MODEL_PATH/mastomys_natalensis.pt" ]; then
    echo -e "${GREEN}✓ Custom model found${NC}"
elif [ -f "$MODEL_PATH/yolov8n.pt" ]; then
    echo -e "${GREEN}✓ YOLOv8n model found${NC}"
else
    echo -e "${YELLOW}⚠ No model found. Will download YOLOv8n on first run${NC}"
fi

# 5. Check database
echo ""
echo "5️⃣ Checking database configuration..."
if [ -f ".env" ]; then
    if grep -q "DATABASE_URL" .env; then
        echo -e "${GREEN}✓ DATABASE_URL configured${NC}"
    else
        echo -e "${YELLOW}⚠ DATABASE_URL not found in .env${NC}"
    fi
    
    if grep -q "NEXT_PUBLIC_SUPABASE_URL" .env; then
        echo -e "${GREEN}✓ Supabase configured${NC}"
    else
        echo -e "${YELLOW}⚠ Supabase not configured (realtime features disabled)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
fi

# 6. Initialize database
echo ""
echo "6️⃣ Database schema..."
echo "Run this command to initialize the detections table:"
echo "  psql \$DATABASE_URL -f scripts/init-detections-table.sql"
echo ""

# 7. Create temp directories
echo "7️⃣ Creating temp directories..."
mkdir -p temp/uploads
echo -e "${GREEN}✓ Temp directories created${NC}"

# 8. Summary
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Initialize database: psql \$DATABASE_URL -f scripts/init-detections-table.sql"
echo "  2. Start dev server: pnpm dev"
echo "  3. Test inference: POST to /api/detections/inference"
echo "  4. View docs: cat INFERENCE_SETUP.md"
echo ""
echo "Happy detecting! 🧬"
