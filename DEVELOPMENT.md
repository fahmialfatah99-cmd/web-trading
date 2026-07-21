# 🛠️ Development Guide

## Project Structure

```
web trading /
├── backend/
│   ├── main.py                 # FastAPI app + route handlers
│   ├── technical_indicators.py # RSI, MACD, Bollinger, etc.
│   ├── trading_engine.py       # Decision engine + backtesting
│   ├── data_fetcher.py         # Yahoo Finance data + retry logic
│   ├── config.py               # Configuration constants
│   ├── requirements.txt        # Dependencies
│   └── .env.example            # Environment variables
├── index.html                  # Frontend UI
├── start.sh                    # Production launcher
├── dev-start.sh                # Development launcher
├── README.md                   # Quick start
├── README_LENGKAP.md           # Full documentation
├── CHANGELOG.md                # Version history
└── DEVELOPMENT.md              # This file
```

## Module Responsibilities

### main.py
- FastAPI application setup
- CORS configuration
- Route handlers
- Request validation
- Response formatting

### technical_indicators.py
- RSI calculation
- MACD calculation
- Bollinger Bands
- VWAP
- ATR
- ADX
- Stochastic
- Support/Resistance

### trading_engine.py
- Multi-signal analysis
- BUY/SELL/HOLD decision
- Target price calculation
- Stop loss calculation
- SMA crossover backtesting

### data_fetcher.py
- Yahoo Finance API integration
- Retry mechanism
- Data validation
- Error handling

## Development Workflow

### 1. Setup Dev Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test API Endpoints
```bash
# Get stock analysis
curl "http://localhost:8000/api/stock/BBCA?period=1mo"

# Run backtest
curl "http://localhost:8000/api/backtest/BBCA?period=2y"

# Health check
curl "http://localhost:8000/api/health"

# API docs
curl "http://localhost:8000/docs"
```

## Adding New Features

### Example: Add New Indicator

1. **Add to technical_indicators.py:**
```python
@staticmethod
def calculate_new_indicator(prices: List[float]) -> Optional[float]:
    try:
        # Your calculation
        result = ...
        return round(float(result), 2)
    except Exception as e:
        print(f"Error: {e}")
        return None
```

2. **Add to TechnicalIndicators model in main.py:**
```python
new_indicator: Optional[float] = None
```

3. **Call in get_stock_analysis:**
```python
new_ind = analyzer.calculate_new_indicator(closes)
indicators.new_indicator = new_ind
```

4. **Update frontend to display it.**

## Testing

### Manual Testing Checklist
- [ ] Backend starts without errors
- [ ] API /health returns OK
- [ ] Stock data loads correctly
- [ ] All indicators calculated
- [ ] Trading decision generated
- [ ] Frontend displays data
- [ ] Chart renders
- [ ] Mobile responsive

### Test Symbols
```
Popular: BBCA, BBRI, TLKM, ASII, GOTO
Small Cap: Various other IDX stocks
```

## Performance Optimization

### Current Optimizations
- Last 60 candles only (not full history)
- Indicator caching possible
- Async/await for I/O
- Minimal calculations

### Future Optimizations
- Add Redis caching
- Implement WebSocket for real-time updates
- Batch API requests
- Progressive data loading

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Browser Console
Open DevTools (F12) to see:
- API requests/responses
- JavaScript errors
- Network timing

### Backend Logs
```bash
# Watch logs
tail -f backend.log

# Or capture to file
python3 -m uvicorn main:app ... > backend.log 2>&1
```

## Common Issues

### Import Errors
```bash
# Reinstall
pip install --force-reinstall -r requirements.txt
```

### Port Already in Use
```bash
# Use different port
python3 -m uvicorn main:app --port 8001
```

### Yahoo Finance API Down
- Fallback data is generated
- Check API status
- Try different symbol

## Code Style

- Use type hints
- Add docstrings
- Error handling (try-catch)
- Descriptive variable names
- Comments for complex logic

## Deployment

### Production Checklist
- [ ] Remove --reload flag
- [ ] Set proper CORS origins
- [ ] Configure .env variables
- [ ] Use HTTPS
- [ ] Enable logging
- [ ] Monitor performance
- [ ] Setup error alerts

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request
6. Code review & merge

---

**Questions? Open an issue or contact the maintainers!**
