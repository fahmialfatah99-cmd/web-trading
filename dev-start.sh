#!/bin/bash

# Development startup - Backend only
echo "🚀 Starting IDX Stock Terminal Backend (Dev Mode)..."
cd "web trading /backend"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
