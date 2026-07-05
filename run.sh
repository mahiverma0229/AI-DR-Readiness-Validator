#!/bin/bash

echo "🚀 Starting AI DR Readiness Validator..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with Python 3.12..."
    python3.12 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run the application
echo ""
echo "✅ Starting API server..."
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔍 DR Score: http://localhost:8000/api/v1/dr-score"
echo "⚠️  Alerts: http://localhost:8000/api/v1/alerts"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Made with Bob
