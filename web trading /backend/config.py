"""Configuration and constants for trading analysis"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Data Configuration
DATA_CACHE_TTL = 300  # 5 minutes
MAX_RETRIES = 3
TIMEOUT = 30.0

# Trading Configuration
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2
ATR_PERIOD = 14
ADX_PERIOD = 14

# Analysis Configuration
MIN_CANDLES_FOR_ANALYSIS = 50
CONFIDENCE_THRESHOLD = 0.5

# Market Hours (IDX)
MARKET_OPEN = 9  # 9 AM
MARKET_CLOSE = 16  # 4 PM
MARKET_TIMEZONE = "Asia/Jakarta"

# Symbols
IDX_SYMBOLS = [
    "BBCA", "BBRI", "TLKM", "ASII", "GOTO", "INDF",
    "UNVR", "ARHI", "CPIN", "JPFA", "CLAP", "HMSP"
]
