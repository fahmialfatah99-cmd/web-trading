# 🇮🇩 IDX Stock Terminal - Advanced Trading Analysis Platform

**Platform analisa saham real-time dengan indikator teknikal lengkap dan rekomendasi trading otomatis untuk saham Indonesia (IDX)**

---

## 📋 Daftar Isi
1. [Fitur](#fitur)
2. [Requirements](#requirements)
3. [Setup](#setup)
4. [API Endpoints](#api-endpoints)
5. [Indikator Teknikal](#indikator-teknikal)
6. [Algoritma Trading](#algoritma-trading)
7. [Troubleshooting](#troubleshooting)

---

## ✨ Fitur

### 🎯 Data Real-Time
- ✅ Data harga **REAL** dari Yahoo Finance (bukan simulasi)
- ✅ Update otomatis dengan retry logic
- ✅ Support semua saham IDX dengan suffix `.JK`
- ✅ Caching untuk performa optimal

### 📊 Indikator Teknikal Lengkap
- **RSI (14)** - Relative Strength Index untuk oversold/overbought
- **MACD** - Moving Average Convergence Divergence + Signal Line
- **Bollinger Bands** - Upper, Middle, Lower bands
- **VWAP** - Volume Weighted Average Price
- **ATR** - Average True Range untuk volatility
- **ADX** - Average Directional Index untuk trend strength
- **Stochastic** - K & D untuk momentum
- **Support & Resistance** - Pivot Points, R1/R2, S1/S2

### 🤖 Trading Decision Engine
- ✅ Rekomendasi **BUY / SELL / HOLD** berbasis multi-indicator
- ✅ Confidence level 0-100%
- ✅ Target price & Stop loss otomatis
- ✅ Mode Daily dan Monthly
- ✅ Signal explanation untuk setiap rekomendasi

### 📈 Backtesting
- ✅ SMA Crossover (10/30) testing
- ✅ Calculate: Total Return, Sharpe Ratio, Max Drawdown, Win Rate
- ✅ Historical performance validation

### 💬 Sentiment Analysis
- ✅ Analisa sentimen berita finansial
- ✅ Keyword detection (Positive/Negative/Neutral)
- ✅ Confidence scoring

### 🎨 UI Modern
- ✅ Dark mode design
- ✅ Real-time chart dengan Chart.js
- ✅ Responsive untuk desktop & mobile
- ✅ Smooth animations & transitions

---

## 📦 Requirements

### Backend (Python)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
numpy==1.24.3
pandas==2.1.3
python-dotenv==1.0.0
```

### Frontend
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Chart.js 4.4.0 (CDN)
- Font Awesome 6.4.0 (CDN)

---

## 🚀 Setup & Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/fahmialfatah99-cmd/web-trading.git
cd "web trading "
```

### 2. Setup Backend
```bash
cd backend
pip install -r requirements.txt

# Copy .env.example ke .env (opsional)
cp .env.example .env
```

### 3. Jalankan Backend

**Option A: Script Otomatis**
```bash
cd "/workspace/web trading "
./start.sh
```

**Option B: Manual**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend running di: `http://localhost:8000`

### 4. Buka Frontend
```bash
# Buka file index.html di browser
open "web trading /index.html"
# atau
firefox "web trading /index.html"
```

✅ Frontend running di: `file:///.../web trading /index.html`

---

## 🔌 API Endpoints

### 1. Get Stock Analysis (UTAMA)
```
GET /api/stock/{symbol}

Parameters:
  - symbol: Kode saham (BBCA, BBRI, TLKM, dll)
  - period: 1mo, 3mo, 1y, 2y (default: 1mo)
  - mode: daily atau monthly (default: daily)

Response:
{
  "symbol": "BBCA",
  "current_price": 9650.0,
  "prev_close": 9600.0,
  "change_percent": 0.52,
  "candles": [...],
  "indicators": {
    "rsi_14": 55.2,
    "macd": 0.0045,
    "macd_signal": 0.0038,
    "vwap": 9620.5,
    "atr": 120.5,
    "adx": 45.2,
    "bollinger_upper": 9800.0,
    "bollinger_middle": 9650.0,
    "bollinger_lower": 9500.0,
    "stochastic_k": 65.3,
    "support_1": 9450.0,
    "resistance_1": 9850.0
  },
  "trading_decision": {
    "action": "BUY",
    "confidence": 0.78,
    "reason": "RSI Weak; MACD Bullish; Price > VWAP",
    "target_price": 10808.0,
    "stop_loss": 9360.5
  },
  "prediction_interval": {
    "lower_95": 9450.0,
    "upper_95": 9850.0
  }
}
```

### 2. Sentiment Analysis
```
POST /api/sentiment?text=<berita>

Example:
POST /api/sentiment?text=BBCA naik 5% karena kinerja positif

Response:
{
  "label": "Positive",
  "score": 0.75,
  "confidence": 0.75,
  "keywords": ["naik", "positif"]
}
```

### 3. Backtest Strategy
```
GET /api/backtest/{symbol}

Parameters:
  - symbol: Kode saham
  - period: 1mo, 3mo, 1y, 2y (default: 2y)
  - strategy: sma_crossover (default)

Response:
{
  "total_return": 0.2534,
  "sharpe_ratio": 1.45,
  "max_drawdown": 0.0823,
  "win_rate": 0.67,
  "trades_count": 15,
  "profitable_trades": 10
}
```

### 4. Health Check
```
GET /api/health

Response:
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00",
  "service": "IDX Stock Terminal"
}
```

### 5. Available Symbols
```
GET /api/symbols

Response:
{
  "symbols": ["BBCA", "BBRI", "TLKM", "ASII", ...],
  "count": 12
}
```

---

## 📊 Indikator Teknikal

### RSI (Relative Strength Index)
- **Period:** 14 hari
- **Range:** 0-100
- **Signals:**
  - RSI < 30: **Oversold** (bullish) → BUY
  - RSI < 40: Weak (weak bullish)
  - RSI > 70: **Overbought** (bearish) → SELL
  - RSI > 60: Strong (strong bearish)
- **Formula:** RSI = 100 - (100 / (1 + RS))
  - RS = Avg Gain / Avg Loss

### MACD (Moving Average Convergence Divergence)
- **Fast EMA:** 12 hari
- **Slow EMA:** 26 hari  
- **Signal Line:** 9 hari EMA dari MACD
- **Signals:**
  - MACD > Signal: **Bullish** → BUY
  - MACD < Signal: **Bearish** → SELL
  - Histogram: MACD - Signal (positif/negatif trend strength)

### Bollinger Bands
- **Period:** 20 hari
- **Standard Deviation:** 2σ
- **Components:**
  - Upper = SMA(20) + 2σ
  - Middle = SMA(20)
  - Lower = SMA(20) - 2σ
- **Signals:**
  - Price < Lower BB: Oversold → BUY
  - Price > Upper BB: Overbought → SELL

### VWAP (Volume Weighted Average Price)
- **Formula:** VWAP = Σ(Price × Volume) / Σ(Volume)
- **Signals:**
  - Price > VWAP: Bullish → BUY
  - Price < VWAP: Bearish → SELL

### ATR (Average True Range)
- **Period:** 14 hari
- **Use:** Mengukur volatility
- **High ATR:** High volatility
- **Low ATR:** Low volatility
- **ATR% = (ATR / Close) × 100**

### ADX (Average Directional Index)
- **Period:** 14 hari
- **Range:** 0-100
- **Strength:**
  - ADX < 20: Weak trend
  - ADX 20-40: Moderate trend
  - ADX > 40: Strong trend

### Stochastic Oscillator
- **K Period:** 14 hari
- **D Period:** 3 hari SMA dari K
- **Range:** 0-100
- **Signals:**
  - K < 20: Oversold
  - K > 80: Overbought

### Support & Resistance (Pivot Points)
- **Pivot = (High + Low + Close) / 3**
- **R1 = 2 × Pivot - Low** (1st Resistance)
- **R2 = Pivot + (High - Low)** (2nd Resistance)
- **S1 = 2 × Pivot - High** (1st Support)
- **S2 = Pivot - (High - Low)** (2nd Support)

---

## 🤖 Algoritma Trading Decision

### Signal Scoring
Setiap indikator memberikan score:

```
BUY Signals:
- RSI < 30: +2.0 points
- RSI < 40: +1.0 point
- MACD Bullish: +2.0 points
- Price > VWAP: +1.0 point
- Price < Lower BB: +1.5 points
- Stochastic < 20: +1.0 point
- Near Support: +0.5 point

SELL Signals:
- RSI > 70: +2.0 points
- RSI > 60: +1.0 point
- MACD Bearish: +2.0 points
- Price < VWAP: +1.0 point
- Price > Upper BB: +1.5 points
- Stochastic > 80: +1.0 point
- Near Resistance: +0.5 point
```

### Decision Logic
```python
if buy_strength > sell_strength:
    action = "BUY"
    confidence = min(0.95, 0.5 + (buy_strength / total_strength))
elif sell_strength > buy_strength:
    action = "SELL"
    confidence = min(0.95, 0.5 + (sell_strength / total_strength))
else:
    action = "HOLD"
    confidence = 0.5
```

### Target & Stop Loss
```
MODE DAILY:
  - BUY Target: Current × 1.12 (12% upside)
  - BUY SL: Current × 0.97 (3% downside)
  - SELL Target: Current × 0.88 (12% downside)
  - SELL SL: Current × 1.03 (3% upside)

MODE MONTHLY:
  - BUY Target: Current × 1.08 (8% upside)
  - BUY SL: Current × 0.95 (5% downside)
  - SELL Target: Current × 0.92 (8% downside)
  - SELL SL: Current × 1.05 (5% upside)
```

---

## 📁 Struktur Project

```
web trading /
├── backend/
│   ├── main.py                    # FastAPI application utama
│   ├── technical_indicators.py    # Kalkulator indikator teknikal
│   ├── trading_engine.py          # Decision engine & backtesting
│   ├── data_fetcher.py            # Yahoo Finance integration
│   ├── config.py                  # Configuration & constants
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment variables template
├── index.html                     # Frontend UI (modern design)
├── start.sh                       # Launch script
├── README.md                      # Quick start guide
├── README_LENGKAP.md             # Dokumentasi lengkap (file ini)
└── .gitignore
```

---

## 🐛 Troubleshooting

### Problem: "Connection refused" saat load data
**Solution:**
1. Pastikan backend running: `http://localhost:8000/api/health`
2. Check CORS settings di main.py (sudah allow *)
3. Check firewall port 8000

### Problem: "Stock data not found"
**Solution:**
1. Pastikan symbol valid (suffix .JK otomatis ditambah)
2. Cek Yahoo Finance API status
3. Try dengan symbol populer: BBCA, BBRI, TLKM
4. Pastikan koneksi internet stabil

### Problem: Slow response
**Solution:**
1. Reduce period (gunakan 1mo instead of 2y)
2. Check internet speed
3. Clear browser cache
4. Restart backend

### Problem: ModuleNotFoundError
**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# atau specific modules
pip install fastapi uvicorn pydantic httpx numpy
```

### Problem: Indikator menunjukkan "-"
**Solution:**
1. Butuh minimal 50 candles untuk analisis
2. Wait 5-10 seconds untuk data loading
3. Cek error di browser console (F12)
4. Restart aplikasi

---

## 📈 Contoh Penggunaan

### Analisa BBCA
```
1. Buka index.html
2. Ketik "BBCA" di search box
3. Click LOAD
4. Tunggu chart & indikator loaded
5. Lihat recommendation di sidebar:
   - Action: BUY/SELL/HOLD
   - Target Price
   - Stop Loss
```

### Backtest Strategy
```bash
curl "http://localhost:8000/api/backtest/BBCA?period=2y&strategy=sma_crossover"

# Response:
{
  "total_return": 0.2534,
  "sharpe_ratio": 1.45,
  "max_drawdown": 0.0823,
  "win_rate": 0.67,
  "trades_count": 15
}
```

---

## ⚠️ Disclaimer

✋ **PENTING:**
- Hasil analisis adalah untuk referensi saja
- **BUKAN rekomendasi investasi profesional**
- Trading saham memiliki risiko kehilangan modal
- Lakukan riset mendalam sebelum membeli/menjual
- Konsultasi dengan financial advisor jika diperlukan
- Past performance ≠ Future results

---

## 📞 Support

Untuk issue, feature request, atau bug report:
- GitHub Issues: [link]
- Email: fahmialfatah99@gmail.com

---

## 📄 License

MIT License - Bebas digunakan untuk personal & komersial

---

**Made with ❤️ for Indonesian Traders**

*Last Updated: 2026-07-21*
