#!/bin/bash

# IDX Stock Terminal - Startup Script
# Start both backend and open frontend

set -e

echo ""
echo "🚀 ================================="
echo "🚀 IDX Stock Terminal v2.0"
echo "🚀 ================================="
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    echo "Please run this script from the root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found"
    echo "Please install Python 3.8+"
    exit 1
fi

echo "✅ Checking requirements..."
cd backend

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Check if dependencies installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting Backend..."
echo "   Running on: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
