#!/bin/bash
# Real connection testing script

echo "🔬 TESTING MNTRK SOVEREIGN GRID CONNECTIONS"
echo "==========================================="

# Check environment variables
if [ -z "$FIREBASE_CREDENTIALS" ]; then
    echo "❌ FIREBASE_CREDENTIALS not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Test Firebase
echo "🔥 Testing Firebase connection..."
python setup/firebase_setup.py

if [ $? -eq 0 ]; then
    echo "✅ Firebase test passed"
else
    echo "❌ Firebase test failed"
    exit 1
fi

# Test Neon
echo "🗄️ Testing Neon PostgreSQL connection..."
python setup/neon_setup.py

if [ $? -eq 0 ]; then
    echo "✅ Neon test passed"
else
    echo "❌ Neon test failed"
    exit 1
fi

echo ""
echo "🎯 ALL CONNECTIONS SUCCESSFUL"
echo "✅ MNTRK Sovereign Grid is ready for deployment"
