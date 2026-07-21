# 🚀 IDX Stock Terminal - Quick Start Guide

## ⚡ 5 Menit Setup

### 1. Clone & Install
```bash
git clone https://github.com/fahmialfatah99-cmd/web-trading.git
cd "web trading "
cd backend
pip install -r requirements.txt
```

### 2. Start Backend
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

✅ Backend running: http://localhost:8000

### 3. Open Frontend
```bash
open "../index.html"
```

✅ Frontend ready: Silakan type kode saham!

---

## 📊 Saham Support

**Populer:**
- BBCA (Bank Central Asia)
- BBRI (Bank Rakyat Indonesia)
- TLKM (Telkom Indonesia)
- ASII (Astra International)
- GOTO (GoTo Gojek Tokopedia)

**Semua saham IDX dengan suffix .JK supported**

---

## 🎯 Main Features

| Feature | Deskripsi |
|---------|----------|
| 📈 Real-time Charts | Data aktual dari Yahoo Finance |
| 🔧 Technical Indicators | RSI, MACD, Bollinger, VWAP, ATR, ADX, Stochastic |
| 🤖 AI Recommendations | BUY/SELL/HOLD dengan confidence scoring |
| 💹 Price Targets | Automatic target & stop loss calculation |
| 📉 Support/Resistance | Pivot points & key levels |
| 🧪 Backtesting | Test strategy dengan historical data |
| 💭 Sentiment Analysis | Analisa sentimen berita |
| 📊 95% Prediction Interval | Range estimation |

---

## 🔗 API Endpoints

### Analyze Stock
```bash
curl "http://localhost:8000/api/stock/BBCA?period=1mo&mode=daily"
```

### Backtest
```bash
curl "http://localhost:8000/api/backtest/BBCA?period=2y"
```

### Health Check
```bash
curl "http://localhost:8000/api/health"
```

---

## 📋 Troubleshooting

**Q: "Connection refused"**
- A: Pastikan backend running di port 8000

**Q: "Stock not found"**
- A: Gunakan symbol yang benar (BBCA, bukan BCA)

**Q: Slow loading**
- A: Gunakan period 1mo atau 3mo, bukan 2y

**Q: Import error**
- A: `pip install --upgrade -r requirements.txt`

---

## 📚 Dokumentasi Lengkap

Lihat `README_LENGKAP.md` untuk:
- Penjelasan semua indikator
- Trading algorithm detail
- API documentation lengkap
- Disclaimer & risk warning

---

**Made with ❤️ for Indonesian Traders**