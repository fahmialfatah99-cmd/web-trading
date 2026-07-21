# 🇮🇩 IDX Stock Terminal - Data Asli

Terminal saham Indonesia dengan **data real-time dari Yahoo Finance**.

## ✅ Fitur

- **Data Asli** dari Yahoo Finance (bukan simulasi)
- **Chart Interaktif** dengan Chart.js
- **Indikator Teknikal Lengkap**:
  - RSI (Relative Strength Index)
  - MACD & Signal
  - VWAP (Volume Weighted Average Price)
  - Ichimoku Cloud (Conversion & Base)
  - Pivot Points, Support & Resistance
- **Prediksi Range** (95% Confidence Interval)
- **Analisa Sentimen Berita** Finansial
- **Quick Buttons** untuk saham populer

## 🚀 Cara Menjalankan

### Metode 1: Script Otomatis
```bash
cd "/workspace/web trading "
./start.sh
```

### Metode 2: Manual
```bash
# 1. Start Backend
cd "/workspace/web trading /backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Buka Frontend
Buka file index.html di browser
```

## 📊 Saham yang Tersedia

Semua saham IDX dengan suffix `.JK`:
- BBCA (Bank Central Asia)
- BBRI (Bank Rakyat Indonesia)
- TLKM (Telkom Indonesia)
- ASII (Astra International)
- GOTO (GoTo Gojek Tokopedia)
- INDF (Indofood Sukses Makmur)
- Dan lain-lain...

## 🔌 API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/api/stock/{symbol}` | GET | Data saham + indikator |
| `/api/sentiment` | POST | Analisa sentimen berita |
| `/api/backtest/{symbol}` | GET | Backtest strategi trading |

## 📁 Struktur File

```
web trading /
├── index.html          # Frontend UI
├── backend/
│   └── main.py         # FastAPI Backend
├── start.sh            # Script startup
└── README.md           # Dokumentasi
```

## 💡 Cara Menggunakan

1. **Buka index.html** di browser
2. **Masukkan kode saham** (contoh: BBCA)
3. **Klik LOAD DATA** atau tekan Enter
4. Lihat chart, indikator, dan prediksi
5. Untuk analisa sentimen: tempel berita finansial → klik "Analisa Sentimen"

## ⚠️ Catatan

- Backend harus berjalan di port 8000
- Data diambil real-time dari Yahoo Finance
- Membutuhkan koneksi internet
- Delay data sesuai dengan free tier Yahoo Finance

---
**Dibuat dengan ❤️ untuk trader Indonesia**
