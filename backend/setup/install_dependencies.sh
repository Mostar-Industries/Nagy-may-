#!/bin/bash
# Real dependency installation script

echo "🔧 Installing MNTRK Sovereign Grid Dependencies"
echo "================================================"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install \
    google-cloud-firestore \
    firebase-admin \
    psycopg2-binary \
    sqlalchemy \
    pandas \
    numpy \
    scikit-learn \
    joblib \
    flask \
    connexion[swagger-ui] \
    flask-cors \
    python-dotenv \
    pydantic \
    uvicorn \
    gunicorn

echo "✅ Dependencies installed successfully"
echo "✅ Virtual environment ready at ./venv"
echo ""
echo "To activate: source venv/bin/activate"
