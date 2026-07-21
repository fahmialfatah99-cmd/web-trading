#!/bin/bash
echo "🚀 Starting IDX Stock Terminal Backend..."
cd "/workspace/web trading /backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 3
echo ""
echo "✅ Backend running at http://localhost:8000"
echo "✅ Open index.html in browser to use the app"
echo ""
echo "API Endpoints:"
echo "  - GET  http://localhost:8000/api/stock/{symbol}"
echo "  - POST http://localhost:8000/api/sentiment?text=..."
echo "  - GET  http://localhost:8000/api/backtest/{symbol}"
echo ""
wait
